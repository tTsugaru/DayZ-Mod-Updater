import subprocess
import shutil
import os

# App id in this case its the id for DayZ
app_id = 221100

# Username for steamcmd login (Please note that you should have been logged in once in the steamcmd else this script won't work properly, will be coming later)
steam_login_username = "username"

# Root directory of the server (Default should be where your dayzserver file is located)
# e.g. "/home/username/dayzserver"
root_dir = "/home/username/dayzserver"

# The directory where mods and keys are located, needs to be inside of the root directory
# e.g. "/home/username/dayzserver/serverfiles" then this property would be "serverfiles" ("/home/username/dayzserver/" will be added automatically because it was defined above) 
server_files_dir = "serverfiles"

# Temporary Directory for steamcmd to download workshop items to. (can be every name doesnt really matter)
steamcmd_download_dir_name = "steam-mods"

# This property will add more prints while doing stuff so you can see whats happening
debug = False

# Indicates if the servers mods and keys directories should be cleared before moving the new/updated mods.
should_clear = True

# Workshop items that you want to download
workshop_item_ids = [
    # Bets approach here is to write the name and link to the mod so you dont loose it
    # e.g. 1559212036, # CF Framework - https://steamcommunity.com/sharedfiles/filedetails/?id=1559212036
]

force_install_dir = f"{root_dir}/{steamcmd_download_dir_name}"
steam_mods_dir = f"{root_dir}/{steamcmd_download_dir_name}/steamapps/workshop/content/{app_id}"

dayz_server_mods_dir = f"{root_dir}/{server_files_dir}/mods"
dayz_server_keys_dir = f"{root_dir}/{server_files_dir}/keys"

# Building the SteamCMD command to execute
def build_steam_command():
    """Creates the SteamCMD command that should be executed to download the workshop content"""

    print("[Command-Service] Creating SteamCMD command to execute.")
    steamcmd_command = f"steamcmd +force_install_dir {force_install_dir} +login {steam_login_username}" 
    for workshop_item_id in workshop_item_ids: steamcmd_command += f" +workshop_download_item {app_id} {workshop_item_id}"
    steamcmd_command += " +quit"
    print("[Command-Service] Done!", steamcmd_command)
    return steamcmd_command

# Running SteamCMD
def run_steamcmd(command: str, debug: bool = False):
    """Executes SteamCMD and downloads the workshop items with the created SteamCMD command"""

    print("[Download-Service] SteamCMD workshopitems will be downloaded now! Please hold tight, could take some time.")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, encoding="utf-8")
    if debug:
        for line in process.stdout: print(line, end="\n")
    process.wait()
    print("[Download-Service] Done.")

# Clearing the mods and keys directories of the server
def clear_mods_and_keys():
    """Clears the mods and keys directories of the server"""

    # Checking if the keys directory exists, then checking if there are keys to remove, if yes they will be removed
    if os.path.exists(dayz_server_keys_dir):
        server_keys = os.listdir(dayz_server_keys_dir)
        if len(server_keys) > 0:
            [os.remove(f"{dayz_server_keys_dir}/{server_key}") for server_key in server_keys]
            print("[Clean-Service] Removed all existing keys in the servers keys directory.")

    # Checking if the mods directory exists, then checking if there are mods to remove, if yes they will be removed
    if os.path.exists(dayz_server_mods_dir):
        server_mods = os.listdir(dayz_server_mods_dir)
        if len(server_mods) > 0:
            [shutil.rmtree(f"{dayz_server_mods_dir}/{server_mod}") for server_mod in server_mods]
            print("[Clean-Service] Removed all existing mods in the servers mods directory.")

# Setting up for file moving
def move_mods_to_server(debug: bool = False):
    """Moves the mods and keys to the corresponding server directories"""

    print("[Move-Service] Starting to move the Mods and their corresponding Keys.")
    # Getting all mods inside of the steam download directory
    all_mod_dirs = os.listdir(steam_mods_dir)

    # Going through all of the downloaded mods
    for mod_dir in all_mod_dirs: 

        # Checking if the found mod is inside of the array that needed to be downloaded
        if int(mod_dir) in workshop_item_ids:
            # Creating the current mod location Path
            current_mod_location = f"{steam_mods_dir}/{mod_dir}"
            # Creating the destination path for the mod
            dayz_server_mod_path = f"{dayz_server_mods_dir}/{mod_dir}"

            # Lowercasing modfiles to find right name for keys directory cause it could be uppercased
            mod_files = os.listdir(current_mod_location)
            mod_files_lowercased = [mod_file.lower() for mod_file in mod_files]
            mod_key_dir = mod_files[mod_files_lowercased.index("keys")]
            mod_key_dir_path = f"{current_mod_location}/{mod_key_dir}"

            # Checking if the Keys directory exists
            if os.path.exists(dayz_server_keys_dir):
                # Getting all mod keys
                mod_keys = os.listdir(mod_key_dir_path)
                # Going through all of them
                for mod_key in mod_keys:
                    # Creating the current mod key location path
                    mod_key_path = f"{mod_key_dir_path}/{mod_key}"
                    # Creating the destination path for the key
                    mod_key_destination_path = f"{dayz_server_keys_dir}/{mod_key}"

                    # Checking if the key already exists, if yes then remove it
                    if os.path.exists(mod_key_destination_path):
                        os.remove(mod_key_destination_path)
                        if debug:
                            print("[Move-Service] Removed already found Key", mod_key)

                    # Copy the key to the servers key directory
                    copyfilepath = shutil.copyfile(mod_key_path, mod_key_destination_path)

                    if debug:
                        print("[Move-Service] Copied Key to: ", copyfilepath)


            # Checking if the mod already is on the server, if yes removing it
            if os.path.exists(dayz_server_mod_path):
                shutil.rmtree(dayz_server_mod_path)

            # Copy the new/updated mod to the server mods folder
            copypath = shutil.copytree(current_mod_location, dayz_server_mod_path)

            if debug:
                print("[Move-Service] Copied mod to: ", copypath)
    print("[Move-Service] Copied all keys to the server keys directory.", dayz_server_keys_dir)
    print("[Move-Service] Copied all mods to the server mods directory.", dayz_server_mods_dir)
    print("[Move-Service] Done!")

# Cleans the created directory from SteamCMD
def cleanup():
    """Cleans the created directory from SteamCMD to stay clean"""
    steamcmd_dir = f"{root_dir}/{steamcmd_download_dir_name}"

    if os.path.exists(steamcmd_dir):
        shutil.rmtree(steamcmd_dir)
        print("[Clean-Service] Removed created steam directory.")

    print("[Clean-Service] Done!")

#################################################
# Executing the above implemented functions
#################################################

steamcmd_command = build_steam_command()
run_steamcmd(steamcmd_command, debug=debug)

if should_clear:
    clear_mods_and_keys()

move_mods_to_server(debug=debug)

cleanup()