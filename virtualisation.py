import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def import_ova(ova):
    try:
        if not os.path.exists(ova):
            messagebox.showerror("Erreur", "Le fichier OVA n'existe pas.")
            return None
        vm_name = os.path.splitext(os.path.basename(ova))[0]
        check_vm = subprocess.run(["VBoxManage","list","vms"],capture_output=True,text=True)
        if vm_name in check_vm.stdout:
            messagebox.showinfo("Information", "La machine virtuelle existe déjà.")
            return vm_name
        messagebox.showinfo("Information", "Importation de l'OVA en cours...")
        subprocess.run(["VBoxManage", "import", ova],check=True)
        messagebox.showinfo("Succès", "Machine virtuelle importée avec succès.")
        return vm_name
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'importation : {e}")
        return None
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inconnue : {e}")
        return None

def clone(template, new):
    try:
        check_template = subprocess.run(["VBoxManage", "list", "vms"], capture_output=True, text=True)
        if template not in check_template.stdout:
            messagebox.showerror("Erreur", "Le modèle de machine virtuelle n'existe pas.")
            return
        messagebox.showinfo("Information", "Clonage de la machine virtuelle en cours...")
        subprocess.run(["VBoxManage","clonevm",template,"--name",new,"--register","--mode","all"],check=True)
        messagebox.showinfo("Succès", "Clonage effectué avec succès.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur lors du clonage : {e}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inconnue : {e}")

def create_vm(vm_name, iso_path, ram_size, cpu_count, disk_size):
    try:
        messagebox.showinfo("Information", f"Création de la VM '{vm_name}' en cours...")
        run_command(f"VBoxManage createvm --name {vm_name} --register")

        messagebox.showinfo("Information", f"Configuration de la VM '{vm_name}' en cours...")
        run_command(f"VBoxManage modifyvm {vm_name} --memory {ram_size} --cpus {cpu_count} --ostype Ubuntu_64")

        messagebox.showinfo("Information", "Création du disque virtuel...")
        disk_path = os.path.join(os.getcwd(), f"{vm_name}.vdi")
        run_command(f"VBoxManage createhd --filename {disk_path} --size {disk_size}")
        run_command(f"VBoxManage storagectl {vm_name} --name 'SATA Controller' --add sata --controller IntelAhci")
        run_command(f"VBoxManage storageattach {vm_name} --storagectl 'SATA Controller' --port 0 --device 0 --type hdd --medium {disk_path}")

        messagebox.showinfo("Information", "Attachement du fichier ISO...")
        run_command(f"VBoxManage storageattach {vm_name} --storagectl 'SATA Controller' --port 1 --device 0 --type dvddrive --medium {iso_path}")

        messagebox.showinfo("Information", "Configuration du réseau...")
        run_command(f"VBoxManage modifyvm {vm_name} --nic1 nat")

        messagebox.showinfo("Information", f"Lancement de la VM '{vm_name}'...")
        run_command(f"VBoxManage startvm {vm_name} --type gui")
        messagebox.showinfo("Succès", "La VM a démarré avec succès.")

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'exécution de la commande : {e.stderr}")
        raise

def on_clonage_button():
    template = entry_template.get()
    new = entry_new_name.get()
    if template and new:
        clone(template, new)
    else:
        messagebox.showwarning("Entrée manquante", "Veuillez remplir tous les champs.")

def on_import_ova_button():
    ova = entry_ova.get()
    new = entry_new_name.get()
    if ova and new:
        vm_name = import_ova(ova)
        if vm_name:
            clone(vm_name, new)
    else:
        messagebox.showwarning("Entrée manquante", "Veuillez remplir tous les champs.")

def on_creation_vm_button():
    vm_name = entry_vm_name.get()
    iso_path = entry_iso_path.get()
    ram_size = entry_ram_size.get()
    cpu_count = entry_cpu_count.get()
    disk_size = entry_disk_size.get()
    
    if vm_name and iso_path and ram_size and cpu_count and disk_size:
        try:
            ram_size = int(ram_size)
            cpu_count = int(cpu_count)
            disk_size = int(disk_size)
            create_vm(vm_name, iso_path, ram_size, cpu_count, disk_size)
        except ValueError:
            messagebox.showwarning("Entrée invalide", "Veuillez entrer des valeurs numériques valides pour la RAM, le nombre de cœurs et la taille du disque.")
    else:
        messagebox.showwarning("Entrée manquante", "Veuillez remplir tous les champs.")

def display_fields(choice):
    for widget in frame.winfo_children():
        widget.grid_forget()

    label_method.grid(row=0, column=0, columnspan=2, pady=10)
    menu.grid(row=1, column=0, columnspan=2)

    if choice == "cloner":
        label_template.grid(row=2, column=0, pady=5)
        entry_template.grid(row=2, column=1, pady=5)
        label_new_name.grid(row=3, column=0, pady=5)
        entry_new_name.grid(row=3, column=1, pady=5)
        button_clonage.grid(row=4, column=0, columnspan=2)
    elif choice == "import_ova":
        label_ova.grid(row=2, column=0, pady=5)
        entry_ova.grid(row=2, column=1, pady=5)
        label_new_name.grid(row=3, column=0, pady=5)
        entry_new_name.grid(row=3, column=1, pady=5)
        button_import_ova.grid(row=4, column=0, columnspan=2)
    elif choice == "create_vm":
        label_vm_name.grid(row=2, column=0, pady=5)
        entry_vm_name.grid(row=2, column=1, pady=5)
        label_iso_path.grid(row=3, column=0, pady=5)
        entry_iso_path.grid(row=3, column=1, pady=5)
        label_ram_size.grid(row=4, column=0, pady=5)
        entry_ram_size.grid(row=4, column=1, pady=5)
        label_cpu_count.grid(row=5, column=0, pady=5)
        entry_cpu_count.grid(row=5, column=1, pady=5)
        label_disk_size.grid(row=6, column=0, pady=5)
        entry_disk_size.grid(row=6, column=1, pady=5)
        button_creation_vm.grid(row=7, column=0, columnspan=2)

def on_menu_change(choice):
    display_fields(choice)

root = tk.Tk()
root.title("Gestion des Machines Virtuelles")

frame = tk.Frame(root)
frame.pack(padx=200, pady=100)

label_method = tk.Label(frame, text="Menu")

programme_var = tk.StringVar()
programme_var.set("")

menu = tk.OptionMenu(frame, programme_var, "cloner", "import_ova", "create_vm", command=on_menu_change)

button_clonage = tk.Button(frame, text="Clonage", command=on_clonage_button)
button_import_ova = tk.Button(frame, text="Importer OVA", command=on_import_ova_button)
button_creation_vm = tk.Button(frame, text="Créer une VM", command=on_creation_vm_button)

label_template = tk.Label(frame, text="Nom du modèle:")
label_new_name = tk.Label(frame, text="Nom du nouveau fichier:")
label_ova = tk.Label(frame, text="Chemin du fichier OVA:")
label_vm_name = tk.Label(frame, text="Nom de la VM:")
label_iso_path = tk.Label(frame, text="Chemin du fichier ISO:")
label_ram_size = tk.Label(frame, text="RAM (Mo):")
label_cpu_count = tk.Label(frame, text="Nombre de cœurs CPU:")
label_disk_size = tk.Label(frame, text="Taille du disque (Mo):")

entry_template = tk.Entry(frame)
entry_new_name = tk.Entry(frame)
entry_ova = tk.Entry(frame)
entry_vm_name = tk.Entry(frame)
entry_iso_path = tk.Entry(frame)
entry_ram_size = tk.Entry(frame)
entry_cpu_count = tk.Entry(frame)
entry_disk_size = tk.Entry(frame)

display_fields("")

root.mainloop()
