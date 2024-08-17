# Spotify Advanced Tool

This repository contains the **Spotify Advanced Tool**, developed in Python 3.10.11. The tool uses the Spotify public API to manage playlists, allowing you to add and delete songs in an advanced manner. Below, you will find detailed instructions on how to configure and use the API.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [References](#references)

## Installation

To install and run the code, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/paulomaateus/spotify-advanced-tool.git
   cd spotify-advanced-tool
   ```

2. Create a virtual environment (optional, but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Configuration

To ensure the API works correctly, you need to configure server parameters.

1. Rename the `sample.env` file to `.env`.
2. Edit the `.env` file and add the following variables:
   - `SERVER_IP`: The IP address where the server will be hosted. For local development, you can set this to `localhost`.
   - `SERVER_PORT`: The port number where the server will be accessible. For local development, you can set this to `8000`.

## Usage

To access all the functionalities of the API, follow these steps:

1. **Access the login route**: Use the `/login` endpoint with `client_id` and `client_secret` as query parameters. For example:
   ```
   GET /login?client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET
   ```
   This request will initiate the OAuth2 authorization process with Spotify.

2. **Authorize the application**: You will be redirected to a Spotify OAuth2 authorization page. Follow the prompts to authorize the application to access your Spotify account.

3. **Access the API**: Once the authorization is complete, all other API endpoints will be available for use.

## Endpoints

Below are the main endpoints of the API:

### Authorization

- **Login**
  - **Endpoint:** `/login`
  - **Method:** `GET`
  - **Description:** Initiates the user's authorization process on Spotify.

- **Callback**
  - **Endpoint:** `/callback`
  - **Method:** `GET`
  - **Description:** Callback for Spotify authorization.

### Tracks

- **Track Information**
  - **Endpoint:** `/faixa/{musica_id}`
  - **Method:** `GET`
  - **Description:** Returns information about a specific track.

### Albums

- **Album Tracks**
  - **Endpoint:** `/album/{url_album}`
  - **Method:** `GET`
  - **Description:** Returns the tracks of a specific album.

### Artists

- **Artist Albums**
  - **Endpoint:** `/artista/{url_artista}/albuns`
  - **Method:** `GET`
  - **Description:** Returns the albums of a specific artist.

- **Artist's Top Tracks**
  - **Endpoint:** `/artista/{url_artista}/melhores-musicas`
  - **Method:** `GET`
  - **Description:** Returns the most popular tracks of a specific artist.

### Playlists

- **Add Artist Tracks to Playlist**
  - **Endpoint:** `/playlists/{id_playlist}/artists`
  - **Method:** `POST`
  - **Description:** Adds tracks from an artist to a playlist.

## References

- [Spotify Web API Getting Started](https://developer.spotify.com/documentation/web-api/tutorials/getting-started)

## Contributing

Contributions are welcome! Feel free to open issues and pull requests on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
