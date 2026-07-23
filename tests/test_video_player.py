from unittest.mock import MagicMock, patch

from src.ui.components.video_player import VIDEO_PLAYER_MAX_WIDTH, render_video_player


def test_render_video_player_centers_and_limits_width():
    container = MagicMock()
    container.__enter__.return_value = container
    container.__exit__.return_value = False

    with patch("src.ui.components.video_player.st.container", return_value=container) as mock_container, \
         patch("src.ui.components.video_player.st.video") as mock_video, \
         patch("src.ui.components.video_player.st.caption") as mock_caption:
        render_video_player(b"video-data", ".mp4")

    mock_container.assert_called_once_with(horizontal_alignment="center")
    mock_video.assert_called_once_with(
        b"video-data", format="video/mp4", width=VIDEO_PLAYER_MAX_WIDTH
    )
    mock_caption.assert_called_once_with("Vídeo carregado (formato: .mp4)")
