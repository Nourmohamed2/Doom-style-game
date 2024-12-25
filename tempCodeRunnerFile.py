    def play_intro_video(self):
        # Load the intro video
        video_path = "Intro/DOOM-INTRO.mp4"
        print(f"Loading video from: {video_path}")
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Could not open video.")
            self.main_menu = True
            return

        # Get the video's original resolution
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Video resolution: {width}x{height}")

        # Ensure the video is scaled to the desired resolution (1920x1080)
        target_resolution = (1920, 1080)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Rotate the frame 90 degrees counterclockwise to fix the rotation
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # Convert the frame to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Flip the frame vertically to correct the upside-down issue
            frame = cv2.flip(frame, 0)

            # Resize the frame to the target resolution
            frame = cv2.resize(frame, target_resolution)

            # Convert the frame to a Pygame surface
            frame = pg.surfarray.make_surface(frame)

            # Calculate the position to center the video on the screen
            screen_width, screen_height = RES  # Screen resolution
            video_width, video_height = target_resolution  # Video resolution
            x = (screen_width - video_width) // 2
            y = (screen_height - video_height) // 2

            # Fill the screen with black before blitting the video
            self.screen.fill((0, 0, 0))

            # Display the frame centered on the screen
            self.screen.blit(frame, (400, -400))
            pg.display.flip()

            # Handle events to allow quitting during the video
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    cap.release()
                    pg.quit()
                    sys.exit()

        cap.release()
        self.main_menu = True