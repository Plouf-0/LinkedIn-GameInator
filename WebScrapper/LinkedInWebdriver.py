from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():

    login_url = "https://www.linkedin.com/uas/login?session_redirect=%2Fgames%2F&fromSignIn=true&trk=games_nav-header-signin"

    # DONE Open LinkedIn login window with redirection
    driver = webdriver.Firefox()
    driver.get(login_url)
    assert "LinkedIn" in driver.title

    # DONE Wait until page loaded
    time_to_wait_page_loaded = 1
    # DONE Hide google auth elems
    try:
        # Hide alternate-signin-container
        try:
            WebDriverWait(driver, time_to_wait_page_loaded).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "alternate-signin-container")
                )
            )
        except:
            raise Exception("alternate-signin-container not found")
        else:
            _: int = driver.execute_script(
                "(document.getElementsByClassName('alternate-signin-container'))[0].setAttribute('style', 'visibility: hidden');",
                
            )

        # Hide credential_picker_container
        try:
            WebDriverWait(driver, time_to_wait_page_loaded).until(
                EC.presence_of_element_located((By.ID, "credential_picker_container"))
            )
        except:
            raise Exception("credential_picker_container not found")
        else:
            driver.execute_script(
                "document.getElementById('credential_picker_container').setAttribute('style', 'visibility: hidden');"
            )
    except Exception as e:
        print(e)
        print("Problème pour cacher les logins google")
        pass

    # DONE Wait until user logged in
    print("Please login your LinkedIn account")

    time_to_wait_user_login = 600  # 600s = 10 mins
    try:
        WebDriverWait(driver, time_to_wait_user_login).until(
            EC.presence_of_element_located((By.CLASS_NAME, "msg-overlay-list-bubble"))
        )
    except:
        print("User did not login")
        driver.close()

    print("User logged in")

    # DONE Detect which game is lunched and if game not resolved, call the game's resolver

    print("Now select a game to complete")

    time_to_wait_game_selected = 6
    try:
        WebDriverWait(driver, time_to_wait_game_selected).until(
            EC.presence_of_element_located((By.ID, "clock-small"))
        )
    except:
        print("User did not select a game")
        driver.close()
    print("game selected: " + driver.title)

    if "Patches" in driver.title:
        print("Resolver not yet implemented")
    elif "Zip" in driver.title:
        print("Resolver not yet implemented")
    elif "Mini Sudoku" in driver.title:
        print("Resolver not yet implemented")
    elif "Tango" in driver.title:
        print("Resolver not yet implemented")
    elif "Queens" in driver.title:
        print("Resolver not yet implemented")
    elif "Crossclimb" in driver.title:
        print("Resolver not yet implemented")
    elif "Pinpoint" in driver.title:
        print("Resolver not yet implemented")
    else:
        print("Game not recognised")
        driver.close()

    # TODO Come back to the games window

    # For testing purpose
    # while True:
    #     pass

    driver.close()
    return


if __name__ == "__main__":
    main()
