from nonagon_core.infra.mongo.characters_repo import CharactersRepoMongo
from nonagon_core.infra.mongo.quests_repo import QuestsRepoMongo
from nonagon_core.infra.mongo.summaries_repo import SummariesRepoMongo
from nonagon_core.infra.mongo.users_repo import UsersRepoMongo

user_repo = UsersRepoMongo()
chars_repo = CharactersRepoMongo()
quests_repo = QuestsRepoMongo()
summaries_repo = SummariesRepoMongo()
