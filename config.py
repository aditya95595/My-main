from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AppConfig:
    # Path to YOLO model
    model_path: str = "models/best.pt"

    # ADB connection
    # Examples:
    #   "emulator-5554"          (local emulator)
    #   "192.168.1.10:5555"      (wireless ADB to phone)
    #   None / ""                (auto-detect first device)
    adb_device: Optional[str] = None

    # YOLO confidence threshold
    conf: float = 0.5

    # Use GPU for YOLO / EasyOCR (set False on most VPS – they have no GPU)
    gpu: bool = False

    # Retry attempts for detections
    max_retries: int = 4

    # YOLO class labels used across the bot
    ATTACK_BTN_HOME: str = "attack_btn_home"
    FIND_BTN: str = "find_btn"
    ATTACK_BTN: str = "attack_btn"

    # Resource text labels (top bar during search)
    GOLD: str = "gold"
    ELIXIR: str = "elixir"
    D_ELIXIR: str = "d_elixir"

    # Base layout labels
    END_BTN: str = "end_btn"
    S_GOBLIN: str = "s_goblin"
    ELIXIRS: str = "elixirs"
    NXT_BTN: str = "nxt_btn"
    GOLDS: str = "golds"
    D_ELIXIRS: str = "d_elixirs"

    # Post-battle / surrender labels
    SURR_CONF: str = "surr_conf"
    POST_GOLD: str = "post_gold"
    POST_ELIXIR: str = "post_elixir"
    POST_D_ELIXIR: str = "post_d_elixir"
    RETURN_HOME: str = "return_home"
