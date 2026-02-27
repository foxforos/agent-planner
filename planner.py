# Git test commit
# planner.py
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL, DOCS_FOLDER
from models import Project
from datetime import datetime
import json
import os

import logging
logger = logging.getLogger(__name__)

class Planner:
    def __init__(self, memory_path="memory.json"):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.memory_path = memory_path
        self.memory = self.load_memory()

    def load_memory(self):
        logger.info("PLANNER: load_memory start (memory_path=%s)", self.memory_path)
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info("PLANNER: load_memory success (projects=%d)", len(data))
                # Converti ogni dizionario in un oggetto Project
                return [Project.model_validate(item) for item in data]
        except FileNotFoundError:
            logger.warning("PLANNER: load_memory file non trovato (memory_path=%s). Ritorno lista vuota.", self.memory_path)
            return []
        except json.JSONDecodeError as e:
            logger.error("PLANNER: load_memory JSON invalido (memory_path=%s err=%s). Ritorno lista vuota.", self.memory_path, e)
            return []


    def save_memory(self):
        logger.info("PLANNER: save_memory start (memory_path=%s projects=%d)", self.memory_path, len(self.memory))
        
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                # Converti ogni Project in dict serializzabile
                data = [project.model_dump(mode="json") for project in self.memory]
                json.dump(data, f, indent=4, ensure_ascii=False)

            logger.info("PLANNER: save_memory success (memory_path=%s projects=%d)", self.memory_path, len(self.memory))

        except Exception as e:
            logger.error("PLANNER: save_memory failed (memory_path=%s err=%s)", self.memory_path, e)
            raise


    def project_name_exists(self, name: str) -> bool:
        return self.find_project_by_name(name) is not None

    def get_unique_project_name(self, desired_name: str) -> str:
        """
        Policy creazione:
        - se desired_name NON esiste -> ok
        - se esiste -> suffix automatico: nome-2, nome-3, ...
        (case.insensitive)
        """
        base=desired_name.strip()
        if not base:
            return base
        
        if not self.project_name_exists(base):
            return base
        
        i=2
        while True:
            candidate=f"{base}-{i}"
            if not self.project_name_exists(candidate):
                return candidate
            i+=1

    def make_project_filename(self, project_name: str, extension: str) -> str:
        safe_name=project_name.replace(" ","_")
        return f"progetto_{safe_name}.{extension}"







    def generate_plan(self, objective, template_name=None):
      logger.info("PLANNER: generate_plan start")
      # 1) Template di default se non specificato
      if template_name is None:
          template_name="default"


      #2) Costruisci percorso template: templates/<templates_name>.txt
      base_dir=os.path.dirname(__file__)
      template_filename=f"{template_name}.txt"
      template_path=os.path.join(base_dir, "templates", template_filename)

      #3) Se il template non esiste: errore(scelta A)
      if not os.path.exists(template_path):
            logger.warning("PLANNER: generate_plan template non trovato (template=%s path=%s)", template_name, template_path)
            raise FileNotFoundError(f'Template "{template_name}" non trovato: {template_path}') 
    
      #4) Leggi template
      with open(template_path, "r", encoding="utf-8") as f:
        prompt_template=f.read().strip()
 
      #5) Se template vuoto: errore(evita prompt vuoto)
      if not prompt_template:
        logger.warning("PLANNER: generate_plan template vuoto (template=%s path=%s)", template_name, template_path)
        raise ValueError(f'Template "{template_name}" è vuoto.')
    
      #6) Render prompt
      try:
          prompt=prompt_template.format(objective=objective)
      except KeyError as e:
          logger.error("PLANNER: generate_plan placeholder non valido (template=%s err=%s)", template_name, e)
          raise ValueError(f"Template '{template_name}' ha placeholder non valido: {e}. Usa {{objective}}.")

      #7) Chiamata OpenAI
      response=self.client.chat.completions.create(model=MODEL, messages=[{"role":"user", "content": prompt}])
      content=response.choices[0].message.content
      logger.info("PLANNER: generate_plan success (template=%s)", template_name)
      return content
     
    
    def build_project(self, name, objective, filename, format):
        logger.info("PLANNER: build_project start")
        logger.info("PLANNER: build_project succes (name=%s filename=%s format=%s)", name, filename, format)
        return Project(
            name=name,
            objective=objective,
            created_at=datetime.now(),
            filename=filename,
            format=format,
            tags=[]
        )
    
    def list_projects(self):
        """Ritorna tutti i progetti in memoria"""
        return self.memory
    

    def find_project_by_name(self, name: str):
        """
        Cerca un progetto per nome(case insensitive).
        Ritorna l'istanza Project se trovato, altrimenti None.
        """
        target=name.lower().strip()
        for project in self.memory:
            if project. name.lower().strip() == target:
                return project
        return None
    
    def delete_project(self, name: str) -> bool:
        """
        Elimina un progetto per nome (case insensiive).
        - Rimuove il progetto da self.memory
        - Salva la nuova memoria su memory.json
        - Elimina il file associato in DOCS_FOLDER, se esiste

        Ritorna True se il progetto è stato trovato e cancellato, False altrimenti.
        """
        logger.info("PLANNER: delete_project start (name=%s)", name)
        target=name.lower().strip()

        # 1. Trova il progetto
        project_to_delete=None
        for project in self.memory:
            if project.name.lower().strip() == target:
                project_to_delete=project
                break

        if project_to_delete is None:
            logger.warning("PLANNER: delete_project not found (name=%s)", name)
            return False
        
        # 2. Rimuovi dalla memoria in RAM
        self.memory=[p for p in self.memory if p is not project_to_delete]
        
        # 3. Salva la nuova memoria su file
        self.save_memory()

        # 4. Elimina il file associato(se presente)
        if project_to_delete.filename:
            filepath=os.path.join(DOCS_FOLDER, project_to_delete.filename)
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.info("PLANNER: delete_project file removed (path=%s)", filepath)
            except Exception as e:
                logger.warning("PLANNER: delete_project file removal failed (path=%s err=%s)", filepath, e)
                

        logger.info("PLANNER: delete_project success (name=%s filename=%s)", project_to_delete.name, project_to_delete.filename)
        return True
    

         # Rinomina progetto
    def rename_project(self, old_name: str, new_name: str)-> bool:
        """
        Policy rename:
        - se new_name già esiste (e NON è lo stesso progetto) -> BLOCCO con errore
        - altrimenti rinomina (name + filename fisico)

        Ritorna True se rinominato, False se il progetto non esiste.
        In caso di duplicato sul nuovo nome, solleva ValueError
        """

        logger.info("PLANNER: rename_project start (old_name=%s new_name=%s)", old_name, new_name)

        old_target=old_name.lower().strip()
        new_clean=new_name.strip()
        new_target=new_clean.lower()

        #1) Trova il progetto
        project_to_rename=None
        for project in self.memory:
            if project.name.lower().strip()==old_target:
                project_to_rename=project
                break

        if project_to_rename is None:
            logger.warning("PLANNER: rename_project not found (old_name=%s)", old_name)
            return False
        
        #2)Se il nome cambia davvero, controlla duplicati
        # se cambia solo per maiuscole/spazi, lo consideriamo lo stesso progetto
        if new_target !=old_target:
            existing=self.find_project_by_name(new_clean)
            if existing is not None:
                logger.warning("PLANNER: rename_project duplicate name (old_name=%s new_name=%s)", old_name, new_clean)
                raise ValueError(f"Nome progetto già esistente: '{new_clean}'")
            
        #3)Percorsi file
        old_filepath=os.path.join(DOCS_FOLDER, project_to_rename.filename)

        #4)Nuovo filename(stessa estensione del progetto)
        extension=project_to_rename.format
        new_filename=self.make_project_filename(new_clean,extension)
        new_filepath=os.path.join(DOCS_FOLDER, new_filename)

        #5)Rinomina fisica del file su disco
        try:
            if os.path.exists(old_filepath):
                os.rename(old_filepath, new_filepath)
                logger.info("PLANNER: rename_project file renamed (old_path=%s new_path=%s)", old_filepath, new_filepath)
        except Exception as e:
            logger.warning("PLANNER: rename_project file rename failed (old_path=%s new_path=%s err=%s)", old_filepath, new_filepath, e)

        #6)Aggiorna dati in memoria
        project_to_rename.name=new_clean
        project_to_rename.filename=new_filename

        #7)Salva
        self.save_memory()

        logger.info("PLANNER: rename_project success (old_name=%s new_name=%s filename=%s)", old_name, new_clean, new_filename)

        return True




    def search(self, query: str):
        """
        Cerca progetti che contengono la keyword nel titolo o nel contenuto
        """
        
        result= []
        query=query.lower().strip()

        for project in self.memory:
            project_name=project.name.lower().strip()

            # Match sul titolo
            if query in project_name:
                result.append(project)
                continue

            # Percorso del file
            filepath=os.path.join(DOCS_FOLDER, project.filename)

            if not os.path.exists(filepath):
                continue

            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content=f.read().lower()
                    if query in content:
                        result.append(project)
            except Exception:
                continue

        return result
    



    def get_project_content(self, name: str):
        """
        Ritorna il contenuto completo del file associato al progetto.
        Se progetto o file non esistono, ritorna None.
        """
        
        project=self.find_project_by_name(name)
        if not project:
            return None
        
        filepath=os.path.join(DOCS_FOLDER, project.filename)
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None   
        



    def add_tags_to_project(self, project_name: str, tags: list[str]):
        project=self.find_project_by_name(project_name)
        if not project:
            return None
        
        normalized_tags=[]
        for tag in tags:
            t=tag.strip().lower().replace(" ","-")
            if t:
                normalized_tags.append(t)

        if not normalized_tags:
            return[]
        
        added=[]
        for tag in normalized_tags:
            if tag not in project.tags:
                project.tags.append(tag)
                added.append(tag)

        if added:
            self.save_memory()

        return added
                
    


    def remove_tags_from_project(self, project_name: str, tags:list[str]):
        project=self.find_project_by_name(project_name)
        if not project:
            return None
        
        normalized_tags=[]
        for tag in tags:
            t=tag.strip().lower().replace(" ", "-")
            if t:
                normalized_tags.append(t)

        if not normalized_tags:
            return[]
        
        removed=[]
        for tag in normalized_tags:
            if tag in project.tags:
                project.tags.remove(tag)
                removed.append(tag)

        if removed:
            self.save_memory()

        return removed
    


    def filter_projects_by_tags(self, tags: list[str]):
        """
        Ritorna i progetti che contengono TUTTI i tag richiesti (AND).
        -tags: lista di stringhe(input già splittato lato agent)
        -ritorna: lista di Project(può essere vuota)
        """

        #1) Normalizza i tag richiesti
        normalized_tags=[]
        for tag in tags:
            t=tag.strip().lower().replace(" ", "-")
            if t:
                normalized_tags.append(t)

        #Se non ci sono tag validi, non è un errore: ritorna lista vuota
        if not normalized_tags:
            return[]
        
        #2)Filtra progetti che contengono TUTTI i tag richiesti
        result=[]
        for project in self.memory:
            if all(t in project.tags for t in normalized_tags):
                result.append(project)

        return result
    


    def doctor_report(self) -> dict:
        """
        Analizza la coerenza tra memory.json e la cartella DOCS.
        Non modifica nulla.  Restituisce un report strutturato.
        """

        logger.info("PLANNER: doctor_report start")

        report={
        "missing_files": [],
        "orphan_files":[],
        "invalid_records":[],
        "duplicate_names":[],
        "duplicate_filenames":[],
    }

        # -------------------------
        # 1️⃣ Raccolta dati base
        # -------------------------

        memory_projects=self.memory
        memory_filenames=[]
        memory_names=[]

        for project in memory_projects:
           memory_filenames.append(project.filename)
           memory_names.append(project.name)

    # Lista file fisici in DOCS
        try:
            docs_files=os.listdir(DOCS_FOLDER)
        except Exception as e:
            logger.warning("PLANNER: doctor_report docs folder read failed (docs_folder=%s err=%s)", DOCS_FOLDER, e)
            docs_files=[]

        # -------------------------
        # 2️⃣ Missing files
        # -------------------------

        for project in memory_projects:
            filepath=os.path.join(DOCS_FOLDER, project.filename)
            if not os.path.exists(filepath):
                report["missing_files"].append(project.name)

        # -------------------------
        # 3️⃣ Orphan files
        # -------------------------

        for file in docs_files:
            full_path = os.path.join(DOCS_FOLDER, file)

            # ignora directory (es: _orphaned)
            if os.path.isdir(full_path):
                continue

            if file not in memory_filenames:
                report["orphan_files"].append(file)


        # -------------------------
        # 4️⃣ Invalid records
        # -------------------------

        for project in memory_projects:
            if not project.name or not project.filename or not project.format:
                report["invalid_records"].append(project.name)
                continue
            
            # format coerente con estensione?
            if not project.filename.endswith(project.format):
                report["invalid_records"].append(project.name)

        # -------------------------
        # 5️⃣ Duplicati nomi
        # -------------------------

        seen_names=set()     # set è una struttura dati che non permette duplicati
        for name in memory_names:
            normalized=name.lower().strip()
            if normalized in seen_names:
                report["duplicate_names"].append(name)
            else:
                seen_names.add(normalized)

        # -------------------------
        # 6️⃣ Duplicati filename
        # -------------------------

        seen_filenames=set()   # set è una struttura dati che non permette duplicati
        for filename in memory_filenames:
            normalized=filename.lower().strip()
            if normalized in seen_filenames:
                report["duplicate_filenames"].append(filename)
            else:
                seen_filenames.add(normalized)


        logger.info("PLANNER: doctor_report summary "
        "(missing_files=%d orphan_files=%d invalid_records=%d" 
        " duplicate_names=%d duplicate_filenames=%d)",
          len(report["missing_files"]),
            len(report["orphan_files"]),
              len(report["invalid_records"]),
                len(report["duplicate_names"]),
                  len(report["duplicate_filenames"]))


        return report
    



    def doctor_fix(self) -> dict:
        """
        Versione Safe Mode.
        Fix automatici SOLO per:
        - invalid_records(rimozione da memory)
        - orphan_files(spostamento in docs/_orphaned)

        Restituisce un summary finale.
        """

        # Riesegui report aggiornato
        report=self.doctor_report()

        invalid_records=report.get("invalid_records", []) or []
        orphan_files=report.get("orphan_files", []) or []

        logger.info(
            "DOCTOR_FIX start (safe_mode=True) invalid_records=%d orphan_files=%d memory_path=%s docs_folder=%s",
            len(invalid_records),
            len(orphan_files),
            self.memory_path,
            DOCS_FOLDER
        )



        # Costruzione fix plan
        print("\n==============================")
        print("         DOCTOR FIX (SAFE MODE)")
        print("==============================")

        if not invalid_records and not orphan_files:
            print("Nessun fix necessario. Sistema già coerente.")
            logger.info("DOCTOR_FIX: nessun fix necessario. Exit.")
            return {
                "removed_records": [],
                "moved_files": [],
                "backup_path": None
            }
        
        print("\nFix plan:")
        if invalid_records:
            print(f"-Verranno rimossi {len(invalid_records)} invalid_records dalla memoria.")
        if orphan_files:
            print(f"- Verranno spostati {len(orphan_files)} orphan_files in docs/_orphaned/")

        # Conferma utente
        confirm=input("\nConfermi esecuzione fix? (y/n): ").strip().lower()
        logger.info("DOCTOR_FIX: richiesta conferma utente (confirm=%s)", confirm)
        if confirm !="y":
           logger.info("DOCTOR_FIX: conferma ricevuta. Procedo con fix.")
           print("Operazione annullata.")
           logger.info("DOCTOR_FIX: operazione annullata dall'utente. Exit.")
           return {
              "removed_records": [],
              "moved_files": [],
              "backup_path": None
             }  
    
        # Backup obbligatorio memory.json
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"memory_backup_{timestamp}.json"

        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        backup_path = os.path.join(backup_dir, backup_filename)
        logger.info("DOCTOR_FIX: avvio backup memory (backup_path=%s)", backup_path)


        try:
            with open(self.memory_path, "r", encoding="utf-8") as original:
                data=original.read()
            with open(backup_path, "w", encoding="utf-8") as backup:
                backup.write(data)
                logger.info("DOCTOR_FIX: backup creato con successo (backup_path=%s)", backup_path)
        except Exception as e:
            logger.error("DOCTOR_FIX: errore durante backup. Operazione interrotta. err=%s", e)
            print(f"Errore durante backup. Operazione interrotta: {e}")
            return{
                "removed_records": [],
                "moved_files": [],
                "backup_path": None
            }
        
        removed_records=[]
        moved_files=[]

        # Fix invalid_records(rimozione memoria)
        if invalid_records:
            new_memory=[]
            for project in self.memory:
                if project.name in invalid_records:
                    removed_records.append(project.name)
                    logger.warning( "DOCTOR_FIX: record invalido rimosso (name=%s)", project.name)
                else:
                    new_memory.append(project)
            self.memory=new_memory
            self.save_memory()

        # Fix orphan_files(quarantine)
        if orphan_files:
            orphan_folder=os.path.join(DOCS_FOLDER, "_orphaned")
            if not os.path.exists(orphan_folder):
                os.makedirs(orphan_folder)

            for filename in orphan_files:
                source=os.path.join(DOCS_FOLDER, filename)
                destination=os.path.join(orphan_folder, filename)
                try:
                    if os.path.exists(source):
                        os.rename(source, destination)
                        moved_files.append(filename)
                        logger.warning("DOCTOR_FIX: file orfano spostato (source=%s dest=%s)",source,destination)

                except Exception as e:
                    logger.error("DOCTOR_FIX: errore spostamento file orfano (filename=%s source=%s dest=%s err=%s)",filename,source,destination,e)
                    print(f"Errore spostamento file {filename}: {e}")
                    print("Operazione interrotta per sicurezza.")
                    return {
                        "removed_records": removed_records,
                        "moved_files": moved_files,
                        "backup_path": backup_path
                    }
                
        # Summary finale
        print("\n------------------------------")
        print("Doctor Fix completato.")
        print(f"- Record rimossi: {len(removed_records)}")
        print(f"- File spostati: {len(moved_files)}")
        print(f"- Backup creato in: {backup_path}")
        print("------------------------------\n")

        return {
            "removed_records": removed_records,
            "moved_files": moved_files,
            "backup_path": backup_path
        }




    
            
                 
                 
                 


        
    
                
            
      


        



