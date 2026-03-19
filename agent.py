
import sys

from dotenv import load_dotenv
load_dotenv()

from planner import Planner
from doc_builder import save_markdown, save_text

import logging
from logger_config import setup_logging

logger=logging.getLogger(__name__)





def _print_doctor_section(title: str, items: list[str]) -> None:
    print(f"\n📌 {title}")
    if not items:
        print("✅ OK (nessun elemento)")
        return
    
    print(f"⚠️ Trovati: {len(items)}")
    for i, item in enumerate(items, start=1):
        print(f" {i}. {item}")



def print_doctor_report(report: dict) -> None:
    print("\n==============================")
    print("         DOCTOR REPORT")
    print("==============================")

    missing_files=report.get("missing_files", []) or []
    orphan_files=report.get("orphan_files", []) or []
    invalid_records=report.get("invalid_records", []) or[]
    duplicate_names=report.get("duplicate_names", []) or []
    duplicate_filenames=report.get("duplicate_filenames", []) or []

    _print_doctor_section("Missing_files (in memoria ma file assente in docs/)", missing_files)
    _print_doctor_section("Orphan_files (in docs/ ma non referenziati in memoria)", orphan_files)
    _print_doctor_section("Invalid_records (record incoerenti)", invalid_records)
    _print_doctor_section("Duplicate_names (nomi duplicati)", duplicate_names)
    _print_doctor_section("Duplicate_filenames (filename duplicati)", duplicate_filenames)

    issues_count=(
        len(missing_files)
        +len(orphan_files)
        +len(invalid_records)
        +len(duplicate_names)
        +len(duplicate_filenames)
    )

    print("\n------------------------------")
    if issues_count == 0:
        print("Stato: HEALTHY ✅ (0 problemi)")
    else:
        print(f"Stato: ATTENTION ⚠️ ({issues_count} problemi totali)")
        print("------------------------------\n")
    






def main():
    log_path=setup_logging()
    logger.info(f"Logging attivo su file: {log_path}")

    
    if len(sys.argv) < 2:
        print("Uso: python agent.py \"comando\"")
        return

    command = sys.argv[1]
    logger.info("AGENT: comando ricevuto (input=%s)", command)
    planner = Planner()



    if command.lower() == "doctor":
      logger.info("AGENT: branch scelto (action=doctor)")
      report = planner.doctor_report()
      print_doctor_report(report)
      return
    

    if command.lower() == "doctor_fix":
       logger.info("AGENT: branch scelto (action=doctor_fix)")
       planner.doctor_fix()
       return





    if command.lower().startswith("crea progetto"):
         logger.info("AGENT: branch scelto (action=crea_progetto)")
         # flag formato
         is_txt="--txt" in command.lower()

         # rimuove flag per semplificare parsing
         clean_command=command.replace("--txt", "").replace("--TXT", "").strip()

         # split principale dopo "crea progetto:"
         try:
            payload=clean_command.split(":", 1)[1].strip()
         except IndexError:
            print("Errore: specifica un obiettivo ")
            return

         # sp:lit template / objective
         if ":" in payload:
            template_name, objective= payload.split(":", 1)
            template_name=template_name.strip()
            objective=objective.strip()
         else:
            template_name=None
            objective=payload.strip()

         if not objective: 
            print("Errore: specifica un obiettivo valido.")
            return


         # formato file
         extension="txt" if is_txt else "md"

         # Nome progetto unico(suffix automatico), gestito in planner
         desired_name=objective
         unique_name=planner.get_unique_project_name(desired_name)
         if unique_name != desired_name:
            print(f"Nome già esistente. Creato come: {unique_name}")

         # genera piano
         plan=planner.generate_plan(objective=objective, template_name=template_name)

         # nome file
         filename=planner.make_project_filename(unique_name, extension)

         # salvataggio
         if is_txt:
            filepath=save_text(filename, plan)
         else:
            filepath=save_markdown(filename, plan)

         # costruzione progetto
         project= planner.build_project(name=unique_name, objective=objective, filename=filename, format=extension)
         planner.memory.append(project)
         planner.save_memory()

         print(f"Piano creato: {filepath}")
         return

    



    
    if command.lower() == "mostra progetti":
       logger.info("AGENT: branch scelto (action=mostra_progetti)")
       projects = planner.list_projects()

       if not projects:
         print("📭 Nessun progetto salvato.")
         return

       print("\n📌 Progetti salvati:\n")
       for p in projects:
          print(f"- {p.name} ({p.format}) → {p.filename}")
          
       return
    


    if command.lower().startswith("carica progetto"):
       logger.info("AGENT: branch scelto (action=carica_progetto)")
       # Estrarre il nome dopo i due punti
       if ":" not in command:
          print("❌ Devi specificare un nome. Esempio:")
          print('   python agent.py "carica progetto: nome"')
          return
       
       # Estrarre il nome dopo i due punti
       project_name=command.split(":", 1)[1].strip()

       # Controllo che il nome non sia vuoto
       if not project_name:
          print("❌ Devi indicare il nome del progetto dopo i due punti.")
          return
       
       # Cercare il progetto
       project=planner.find_project_by_name(project_name)

       if not project:
          print(f"❌ Nessun progetto trovato con il nome: {project_name}")
          return
       
       # Mostrare metadati
       print("\n📄 DETTAGLI PROGETTO\n")
       print(f"Nome: {project.name}")
       print(f"Formato: {project.format}")
       print(f"File: {project.filename}")
       print(f"Creato il: {project.created_at}")
       print(f"Tags: {project.tags}")

       return



    if command.lower().startswith("elimina progetto"):
         logger.info("AGENT: branch scelto (action=elimina_progetto)")

         # Controllo che ci siano i due punti
         if ":" not in command:
            print("❌ Devi specificare un nome. Esempio:")
            print('    python agent.py "elimina progetto: nome"')
            return

         # Estrarre il contenuto dopo i due punti
         command_body = command.split(":", 1)[1].strip()

         # Modalità dry-run opzionale da CLI
         cli_dry_run = False
         if command_body.endswith("--dry-run"):
            cli_dry_run = True
            command_body = command_body[:-9].strip()

         project_name = command_body

         # Controlla che il nome non sia vuoto
         if not project_name:
            print("❌ Devi indicare il nome del progetto dopo i due punti.")
            return

         # Preview / simulazione
         report = planner.delete_project(project_name, dry_run=True)

         if not report["found"]:
            print(f"❌ Nessun progetto trovato con il nome: {project_name}")
            return

         print("⚠️ Anteprima eliminazione progetto")
         print(f"   Nome progetto: {report['name']}")
         print(f"   File associato: {report['filename']}")
         print(f"   Percorso file: {report['filepath']}")
         print(f"   Eliminerà dalla memoria: {report['will_delete_memory']}")
         print(f"   Eliminerà file fisico: {report['will_delete_file']}")

         # Se l'utente ha chiesto solo dry-run, fermarsi qui
         if cli_dry_run:
            print("ℹ️ Dry-run completato: nessuna modifica eseguita.")
            return

         # Conferma utente prima dell'eliminazione reale
         confirm = input("Confermi eliminazione? (yes/no): ").strip().lower()

         if confirm != "yes":
            print("ℹ️ Operazione annullata.")
            logger.info("AGENT: eliminazione progetto annullata dall'utente (name=%s)", project_name)
            return

         # Eliminazione reale
         result = planner.delete_project(project_name, dry_run=False)

         if result["deleted_memory"]:
            print(f"🗑️ Progetto '{project_name}' eliminato con successo.")
            if result["deleted_file"]:
                  print("📄 Anche il file associato è stato eliminato.")
            elif result["filename"]:
                  print("ℹ️ Nessun file fisico da eliminare oppure file non presente.")
         else:
            print(f"❌ Eliminazione non riuscita per il progetto: {project_name}")

         return
    

    if command.lower().startswith("modifica progetto"):
         logger.info("AGENT: branch scelto (action=modifica_progetto)")
         try:
            payload=command.split(":", 1)[1].strip()
         except IndexError:
           print("Errore: Il formato corretto è -> modifica progetto: nome attuale: nuovo nome")
           return
         
         # payload deve essere: <nome_attuale>: <nuovo nome>
         if ":" not in payload:
            print("Il formato corretto è -> modifica progetto: nome attuale: nuovo nome")
            return
         
         
         old_name, new_name=payload.split(":", 1)
         old_name=old_name.strip()
         new_name=new_name.strip()

         # Controllo validità input
         if not old_name or not new_name:
            print("❌ I nomi non possono essere vuoti.")
            return
         

         try:
            result=planner.rename_project(old_name, new_name)
            if not result:
               print(f"Errore: progetto '{old_name}' non trovato")
               return
         except ValueError as e:
            print(f"Errore: {e}")
            return
         
         print(f"Progetto rinominato da '{old_name}' a '{new_name}'")
         return
    


    if command.lower().startswith("cerca"):
       logger.info("AGENT: branch scelto (action=cerca)")
       if ":" not in command:
          print("❌ Devi specificare la keyword.  Esempio:")
          print('python agent.py "cerca: KEYWORD"')
          return
       
       key_word= command.split(":", 1)[1].strip()

       if not key_word:
           print("❌ La keyword di ricerca non può essere vuota.")
           return


       

       results=planner.search(key_word)

       if not results:
          print("❌ Nessun progetto correlato.")
       else:
          print("\n📌 Progetti correlati:\n")
          for p in results:
             print(f"- {p.name} ({p.format}) -> {p.filename}")

       return
             




    if command.lower().startswith("apri progetto"):
         logger.info("AGENT: branch scelto (action=apri_progetto)")
         if ":" not in command:
            print("❌ Devi specificare un nome. Esempio:")
            print('   python agent.py "apri progetto: nome"')
            return
    
         project_name=command.split(":", 1)[1].strip()

         if not project_name:
            print("❌ Devi indicare il nome del progetto dopo i due punti.")
            return
    
         content=planner.get_project_content(project_name)

         if content is None:
            print(f"❌ Impossibile aprire il progetto: {project_name}")
            print("  (Nome non trovato in memoria o file mancante in docs/)")
            return
         
         print("\n📖 CONTENUTO PROGETTO\n")
         print(content)
         return
    



    if command.lower().startswith("aggiungi tag"):
         logger.info("AGENT: branch scelto (action=aggiungi_tag)")
         parts=command.split(":", 2)
         if len(parts) < 3:
            print("❌ Formato non valido.")
            print('   Usa: python agent.py "aggiungi tag: nome_progetto : tag1, tag2"')
            return
         
         project_name=parts[1].strip()
         tags_payload=parts[2].strip()

         if not project_name:
            print("❌ Devi indicare il nome del progetto.")
            return
         
         if not tags_payload:
            print("❌ Devi indicare almeno un tag.")
            return
         
         tags_list=[t.strip() for t in tags_payload.split(",") if t.strip()]
         if not tags_list:
            print("❌ Nessun tag valido fornito.")
            return
         
         added=planner.add_tags_to_project(project_name, tags_list)

         if added is None:
            print(f'❌ Progetto"{project_name}" non trovato.')
            return
         
         if not added:
            print("ℹ️ Nessun nuovo tag aggiunto (già presenti).")
            return
         
         print(f'✅ Tag aggiunti al progetto "{project_name}":')
         for t in added:
            print(f"-{t}")
         return
    





    if command.lower().startswith("rimuovi tag"):
         logger.info("AGENT: branch scelto (action=rimuovi_tag)")
         parts=command.split(":", 2)
         if len(parts)<3:
            print("❌ Formato non valido.")
            print('   Usa: python agent.py "rimuovi tag: nome_progetto : tag1, tag2"')
            return
         
         project_name=parts[1].strip()
         tags_payload=parts[2].strip()

         if not project_name:
            print("❌ Devi indicare il nome del progetto.")
            return
         
         if not tags_payload:
            print("❌ Devi indicare almeno un tag da rimuovere.")
            return
         
         tags_list=[t.strip() for t in tags_payload.split(",") if t.strip()]
         if not tags_list:
            print("❌ Nessun tag valido fornito.")
            return
         
         removed=planner.remove_tags_from_project(project_name, tags_list)

         if removed is None:
            print(f'❌ Progetto "{project_name}" non trovato.')
            return
         
         if not removed:
            print("ℹ️ Nessun tag rimosso (non presenti o già rimossi).")
            return
         
         print(f'✅ Tag rimossi dal progetto "{project_name}":')
         for t in removed:
            print(f"- {t}")
         return
    




    if command.lower().startswith("filtra tag"):
         logger.info("AGENT: branch scelto (action=filtra_tag)")
         if ":" not in command:
            print("✘ Devi specificare almeno un tag. Esempio:")
            print('   python agent.py "filtra tag: studio, python"')
            return
         
         tags_payload=command.split(":", 1)[1].strip()

         if not tags_payload:
            print("✘ Devi indicare almeno un tag.")
            return
         
         tags_list=[t.strip()for t in tags_payload.split(",") if t.strip()]
         if not tags_list:
            print("✘ Nessun tag valido fornito.")
            return
         
         results=planner.filter_projects_by_tags(tags_list)

         if not results:
            print("✘ Nessun progetto trovato con tutti i tag richiesti.")
         else:
            print("\n📌 Progetti filtrati per tag:\n")
            for p in results:
                  print(f"- {p.name} ({p.format}) -> {p.filename}")

         return
    

    
          
          

       
       


    logger.warning("AGENT: comando non riconosciuto (input=%s)", command)
    print("Comando non riconosciuto")


if __name__ == "__main__":
    main()
