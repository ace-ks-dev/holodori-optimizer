APP_VERSION = "2.2.0"
SCHEMA_VERSION = 2
SOURCE_NAME = "HolodoriDB/holodori-db-eng-diff"
RAW_BASE_URL = "https://raw.githubusercontent.com/HolodoriDB/holodori-db-eng-diff/main/"

RAW_FILES = [
    "Card.json",
    "CardLevel.json",
    "CardLevelLimit.json",
    "CardPotential.json",
    "Character.json",
    "CharacterGrouping.json",
    "LiveActiveSkillLevel.json",
    "LiveActiveSkillEffect.json",
    "LivePassiveSkillLevel.json",
    "LivePassiveSkillEffect.json",
    "LiveSpecialSkillLevel.json",
    "LiveLeaderSkill.json",
    "LiveSkillTrigger.json",
    "LiveSkillEffectTarget.json",
    "LangCard_Eng.json",
    "LangCharacterGrouping_Eng.json",
    "LangGeneratedLiveActiveSkillLevel_Eng.json",
    "LangGeneratedLivePassiveSkillLevel_Eng.json",
    "LangGeneratedLiveSpecialSkillLevel_Eng.json",
    "LangGeneratedLiveLeaderSkill_Eng.json",
]

ATTRIBUTE_LABELS = {
    "CardAttributeType_CARD_ATTRIBUTE_TYPE_ATTRIBUTE_1": "Cute",
    "CardAttributeType_CARD_ATTRIBUTE_TYPE_ATTRIBUTE_2": "Pure",
    "CardAttributeType_CARD_ATTRIBUTE_TYPE_ATTRIBUTE_3": "Happy",
}

ATTRIBUTE_MARKUP = {
    "cute": "CardAttributeType_CARD_ATTRIBUTE_TYPE_ATTRIBUTE_1",
    "pure": "CardAttributeType_CARD_ATTRIBUTE_TYPE_ATTRIBUTE_2",
    "happy": "CardAttributeType_CARD_ATTRIBUTE_TYPE_ATTRIBUTE_3",
}
