import pandas as pd
import logging
import os

from utils import IndentedLogger

logger = IndentedLogger(logging.getLogger(__name__))

class CardFaceConfig:
    def __init__(self, value: str, cost: str, sect: str, name: str,
                 front_image:str, back_image: str):
        self.value = value
        self.cost = cost
        self.sect = sect
        self.name = name
        self.front_image = front_image
        self.back_image = back_image

    def __repr__(self):
        return (f"CardFaceConfig(name='{self.name}', sect='{self.sect}', "
                f"cost='{self.cost}', value={self.value}, "
                f"front='{self.front_image}', back='{self.back_image}'")
    

class CardDeckConfig:
    def __init__(self, card_deck_defs: str):
        self.card_deck = self.load_card_deck_defs(card_deck_defs)

    def load_card_deck_defs(self, card_deck_defs_file: str):
        assert os.path.exists(card_deck_defs_file), \
          f"Unable to find card deck defs file {card_deck_defs_file}"
        df = pd.read_csv(card_deck_defs_file)
        logger.debug(f"card deck defs file columns are: {df.columns}")
        logger.debug(f"card deck defs size is {df.shape}")
        card_deck_list = []
        for row in df.itertuples(index=False):
            logger.debug(f"this row features are: {row._fields}")
            logger.debug(f"card cost info columns are: {[f for f in row._fields if f.startswith('cost')]}")
            cost_array = [getattr(row,cost_code) for cost_code in row._fields 
                            if cost_code.startswith('cost') and getattr(row,cost_code)]
            logger.debug(f"cost array is: {cost_array}")
            cfc = CardFaceConfig(name = row.name,
                           value = row.value,
                           sect = row.sect,
                           cost = cost_array,
                           front_image=row.front,
                           back_image=row.back
                           )
            card_deck_list.append(cfc)
            logger.info(f"configured card: {cfc.name} from sect {cfc.sect}, deck has {len(card_deck_list)} cards")
        return card_deck_list
    
    def __repr__(self):
        return f"[\n{',\n'.join(str(self.card_deck))}]"
    
    def num_cards(self):
        return len(self.card_deck)
        