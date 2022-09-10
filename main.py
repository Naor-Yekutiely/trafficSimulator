from email.policy import default
from tkinter import *
import os
from functools import partial
import subprocess

main_window = Tk()
simulation_options_UI = ["Heavy Traffic",
                         "Option 2", "Option 3", "Option 4"]
simulation_names = ["Heavy_Traffic",
                    "Option_2",
                    "Option_3", "Option_4"]
simulation_paths = [f"{os.getcwd()}/src/SimulationConfig/Heavy_Traffic_Data.json",
                    "path to Option 2",
                    "path to Option 3", "path to Option 4"]
selected_sim_option = StringVar()
selected_sim_Index = IntVar()


def load_main_window():
    title = Label(main_window, text="DTLS simulator", font=("", 20))
    subtitle = Label(main_window, text="!Add Description!")
    title.pack()
    subtitle.pack()
    run_sim_parallel_btn = Button(
        text="Run Simulation", width=15, height=3, command=run_sim_on_click)
    run_sim_parallel_btn.pack()

    selected_sim_option.set(simulation_options_UI[0])
    selected_sim_Index.set(0)

    dropdown = OptionMenu(
        main_window,
        selected_sim_option,
        *simulation_options_UI,
        command=display_selected)

    dropdown.pack(expand=True)
    #option_var = StringVar(self)
    # run_quick_sim_btn = Button(
    #     text="Quick Simulation", width=15, height=3, command=run_sim_on_click)
    # run_quick_sim_btn.pack()


def display_selected(selected_sim):
    selected_index = simulation_options_UI.index(selected_sim)
    selected_sim_option.set(simulation_options_UI[selected_index])
    selected_sim_Index.set(selected_index)


def select_main_options():
    sec_choise = StringVar()
    sec_choise.set("Choose from list:")
    types_list = [1, 2, 3]
    sec_manu = OptionMenu(main_window, sec_choise, *types_list)
    sec_manu.pack()


def clean_selection():
    for widgets in main_window.winfo_children():
        widgets.destroy()


def run_sim_on_click():
    wd = os.getcwd()
    sim_path = f"{wd}/src/simulation_runner.py"
    subprocess.call(
        f"python3 {sim_path} {simulation_paths[selected_sim_Index.get()]} {simulation_names[selected_sim_Index.get()]}", shell=True)
    docker_path = f"{wd}/infrastructure"
    os.chdir(docker_path)
    subprocess.run(['docker-compose', 'down'], check=True)
    os.chdir(wd)


load_main_window()
# select_main_options()
main_window.mainloop()
