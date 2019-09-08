import time

NUM_OF_DAYS_IN_WEEK = 7


class Applicant:

    def __init__(self, id, days_required):
        self.days_required = days_required
        self.id = id

    @staticmethod
    def parse_input(input_string):
        def get_days_required(days_required):
            return [True if day == '1' else False for day in days_required]
        return Applicant(input_string[0:5], get_days_required(input_string[-7:]))

    def __repr__(self):
        return str(self.id) + " / " + str(self.days_required)


class Organization:

    def __init__(self, domain, number_of_resources, initial_applicants):
        self.number_of_resources = number_of_resources
        self.availability = [number_of_resources] * NUM_OF_DAYS_IN_WEEK
        self.get_initial_availability(initial_applicants)
        #print(pre_enrolled_applicants)
        #print(self.availability)
        self.domain = domain
        self.already_selected = []

    def get_selected_applicants(self):
        return ','.join(sorted([x for x in self.already_selected]))

    def accomodate_applicant(self, applicant):
        self.already_selected.append(applicant.id)
        self.update_availability(applicant)

    def update_availability(self, applicant):
        for index, day in enumerate(applicant.days_required):
            if day:
                self.availability[index] -= 1

    def remove_applicant(self, applicant):
        self.already_selected.pop()
        for index, day in enumerate(applicant.days_required):
            if day:
                self.availability[index] += 1

    def can_accomodate(self, applicant):
        for index, day in enumerate(applicant.days_required):
            if day and self.availability[index] == 0:
                return False
        return True

    def get_efficiency(self):
        efficiency = sum([self.number_of_resources - x for x in self.availability])/float(self.number_of_resources*7)
        # print efficiency
        return efficiency

    def can_accomodate_all(self, available_player_ids):
        currently_added = []
        can_accomodate_all = True
        for applicant in self.domain:
            if applicant.id in available_player_ids:
                if self.can_accomodate(applicant):
                    self.accomodate_applicant(applicant)
                    currently_added.append(applicant)
                else:
                    can_accomodate_all = False
        total_efficiency = self.get_efficiency()
        for a in currently_added:
            self.remove_applicant(a)
        return total_efficiency if can_accomodate_all else -1

    def get_initial_availability(self, initial_applicants):
        for applicant in initial_applicants:
            self.update_availability(applicant)


class Game:
    def __init__(self, spla, lahsa):
        self.spla = spla
        self.lahsa = lahsa
        self.available_players_ids = Game.create_available_players(spla.domain, lahsa.domain)
        self.stored_dictionary = dict()

    def add_to_stored_dictionary(self, move, spla_score, lahsa_score):
        spla_selected_applicants = self.spla.get_selected_applicants()
        lahsa_selected_applicants = self.lahsa.get_selected_applicants()
        if (spla_selected_applicants, lahsa_selected_applicants) not in self.stored_dictionary:
            self.stored_dictionary[(spla_selected_applicants, lahsa_selected_applicants)] = (move, spla_score, lahsa_score)

    def get_from_stored_dictionary(self):
        spla_selected_applicants = self.spla.get_selected_applicants()
        lahsa_selected_applicants = self.lahsa.get_selected_applicants()
        if (spla_selected_applicants, lahsa_selected_applicants) in self.stored_dictionary:
            return self.stored_dictionary[(spla_selected_applicants, lahsa_selected_applicants)]
        return None

    @staticmethod
    def create_available_players(spla_domain, lahsa_domain):
        # print "Creating ", set([x.id for x in spla_domain] + [x.id for x in lahsa_domain])
        return set([p.id for p in spla_domain] + [p.id for p in lahsa_domain])

    def spla_plays(self):
        value = self.get_from_stored_dictionary()
        if value:
            return value

        best_move = None
        best_spla_score = float("-inf")
        best_lahsa_score = 0

        store_requirements_dict = {}

        # print self.available_players_ids

        for player in self.spla.domain:
            # print player.id
            # print True if player in self.available_players_ids else False
            if player.id in self.available_players_ids and self.spla.can_accomodate(player):
                # print "Spla plays" + player.id

                ###CHANGE THIS
                #third optimization
                if not store_requirements_dict.get(str(player.days_required)) == None:
                    continue
                else:
                    store_requirements_dict[str(player.days_required)] = 0

                # player is selected and slot is reserved
                self.available_players_ids.remove(player.id)
                self.spla.accomodate_applicant(player)

                (move, spla_score, lahsa_score) = self.lahsa_plays()
                # print spla_score, lahsa_score

                if spla_score > best_spla_score:
                    #print "SPLA plays", player.id
                    best_spla_score = spla_score
                    best_lahsa_score = lahsa_score
                    best_move = player

                # player is removed from availability
                self.available_players_ids.add(player.id)
                self.spla.remove_applicant(player)

                if best_spla_score == 1:
                    return best_move, best_spla_score, best_lahsa_score

        if not best_move:
            best_spla_score = self.spla.get_efficiency()
            best_lahsa_score = self.lahsa_plays_alone(best_spla_score)

        self.add_to_stored_dictionary(best_move, best_spla_score, best_lahsa_score)

        return best_move, best_spla_score, best_lahsa_score

    def lahsa_plays(self):
        value = self.get_from_stored_dictionary()
        if value:
            return value

        best_move = None
        best_spla_score = 0
        best_lahsa_score = float("-inf")

        store_requirements_dict = {}

        for player in self.lahsa.domain:
            # print True if player in self.available_players_ids else False
            if player.id in self.available_players_ids and self.lahsa.can_accomodate(player):
                # print "Lahsa plays" + player.id

                # third optimization
                if not store_requirements_dict.get(str(player.days_required)) == None:
                    continue
                else:
                    store_requirements_dict[str(player.days_required)] = 0

                # player is selected and slot is reservedinsert into stack
                self.available_players_ids.remove(player.id)
                self.lahsa.accomodate_applicant(player)

                (move, spla_score, lahsa_score) = self.spla_plays()
                # print spla_score, lahsa_score

                if lahsa_score > best_lahsa_score:
                    #print "Lahsa picks", player.id
                    best_lahsa_score = lahsa_score
                    best_spla_score = spla_score
                    best_move = player

                # Remove player and update availability
                self.available_players_ids.add(player.id)
                self.lahsa.remove_applicant(player)

                if best_lahsa_score == 1:
                    return best_move, best_spla_score, best_lahsa_score

        if not best_move:
            best_lahsa_score = self.lahsa.get_efficiency()
            #print "spla starts picking alone"
            best_spla_score = self.spla_plays_alone(best_lahsa_score)
            #print "spla picks alone ended"

        self.add_to_stored_dictionary(best_move, best_spla_score, best_lahsa_score)

        return best_move, best_spla_score, best_lahsa_score

    def spla_plays_alone(self, best_lahsa_score):

        value = self.get_from_stored_dictionary()
        if value:
            return value[1]

        # second optimization
        best_spla_score = -1
        score = self.spla.can_accomodate_all(self.available_players_ids)

        store_requirements_dict = {}

        if score != -1:
            best_spla_score = score
        else:
            for player in self.spla.domain:
                if player.id in self.available_players_ids and self.spla.can_accomodate(player):
                    # print "Spla plays alone" + player.id

                    # third optimization
                    if not store_requirements_dict.get(str(player.days_required)) == None:
                        continue
                    else:
                        store_requirements_dict[str(player.days_required)] = 0

                    # Add players and update availability
                    self.available_players_ids.remove(player.id)
                    self.spla.accomodate_applicant(player)

                    spla_score = self.spla_plays_alone(best_lahsa_score)

                    if spla_score > best_spla_score:
                        #print "SPLA plays", player.id
                        best_spla_score = spla_score

                    # Remove player and update availability
                    self.available_players_ids.add(player.id)
                    self.spla.remove_applicant(player)

                    if best_spla_score == 1:
                        return best_spla_score

        if best_spla_score == -1:
            best_spla_score = self.spla.get_efficiency()

        self.add_to_stored_dictionary(None, best_spla_score, best_lahsa_score)

        return best_spla_score

    def lahsa_plays_alone(self, best_spla_score):
        value = self.get_from_stored_dictionary()
        if value:
            return value[2]

        best_lahsa_score = -1
        score = self.lahsa.can_accomodate_all(self.available_players_ids)

        stored_requirements_dict = {}

        if score != -1:
         best_lahsa_score = score
        else:
            for player in self.lahsa.domain:
                if player.id in self.available_players_ids and self.lahsa.can_accomodate(player):
                    # print "lahsa plays alone" + player.id

                    # third optimization
                    if not stored_requirements_dict.get(str(player.days_required)) == None:
                        continue
                    else:
                        stored_requirements_dict[str(player.days_required)] = 0

                    # Update availability
                    self.available_players_ids.remove(player.id)
                    self.lahsa.accomodate_applicant(player)

                    lahsa_score = self.lahsa_plays_alone(best_spla_score)

                    if lahsa_score > best_lahsa_score:
                        print "lahsa picks alone", self.spla.already_selected
                        best_lahsa_score = lahsa_score

                    # Update availability
                    self.available_players_ids.add(player.id)
                    self.lahsa.remove_applicant(player)

                    if best_lahsa_score == 1:
                        return best_lahsa_score

        if best_lahsa_score == -1:
            best_lahsa_score = self.lahsa.get_efficiency()

        self.add_to_stored_dictionary(None, best_spla_score, best_lahsa_score)

        return best_lahsa_score

    def start_game(self):
        (move, spla_score, lahsa_score) = self.spla_plays()
        print "Spla Efficiency, Normalized", spla_score, spla_score * 7 * self.spla.number_of_resources
        print "Lahsa Efficiency, Normalized", lahsa_score, lahsa_score * 7 * self.lahsa.number_of_resources
        print "Output", move.id
        return move


def read_inputs():
    with open('test.txt') as input_file:
        inputs = [line.strip() for line in input_file.readlines()]
    # print inputs
    return inputs


def write_output(output_data):
    output = open('output.txt', 'w')
    output.write(str(output_data).rstrip())
    output.close()


def get_applicant_info_from_id(applicant_string):
    id = applicant_string[:5]
    gender = applicant_string[5]
    age = int(applicant_string[6:9])
    pets = applicant_string[9]
    med = applicant_string[10]
    car = applicant_string[11]
    license = applicant_string[12]
    required = applicant_string[-7:]
    return {'id': id, 'gender': gender, 'age': age, 'pets': pets, 'med': med, 'car': car, 'L': license,
            'required': required}


if __name__ == "__main__":
    start = time.time()

    input = read_inputs()

    bed = int(input[0])
    spaces = int(input[1])
    L_no = int(input[2])
    L_applicants = input[3:3 + L_no]
    S_no = int(input[L_no + 3])
    S_applicants = input[L_no + 4:L_no + 4 + S_no]
    applicants = input[L_no + S_no + 4]
    applicants_list = input[-int(applicants):]
    applicants_list = sorted(applicants_list, key=lambda x: int(x[:5]))

    lahsa_applicants = []
    spla_applicants = []
    initial_selected_applicants = []

    for applicant in applicants_list:
        if applicant[:5] in S_applicants:
            initial_selected_applicants.append(applicant)
        elif applicant[:5] in L_applicants:
            initial_selected_applicants.append(applicant)

    l_applicants = []
    s_applicants = []

    for applicant in applicants_list:
        parsed_appplicant = Applicant.parse_input(applicant)
        if parsed_appplicant.id in L_applicants:
            l_applicants.append(parsed_appplicant)
            continue
        if parsed_appplicant.id in S_applicants:
            s_applicants.append(parsed_appplicant)
            continue
        d = get_applicant_info_from_id(applicant)
        if d.get('car') == 'Y' and d.get('L') == 'Y' and d.get('med') == 'N':
            spla_applicants.append(Applicant.parse_input(applicant))
        if d.get('age') > 17 and d.get('gender') == 'F' and d.get('pets') == 'N':
            lahsa_applicants.append(Applicant.parse_input(applicant))

    # SPLA object
    spla_object = Organization(spla_applicants, spaces, s_applicants)
    print "Spla Applicants", spla_applicants
    # print [x.id for x in spla_object.domain]
    # LAHSA object
    lahsa_object = Organization(lahsa_applicants, bed, l_applicants)
    print "Lahsa Applicants", lahsa_applicants
    # print lahsa_object.domain
    print "Lahsa initially", lahsa_object.availability
    print "Spla initially", spla_object.availability
    # Game
    g = Game(spla_object, lahsa_object)
    the_one_who_lived = g.start_game()
    write_output(the_one_who_lived.id)

    end_time = time.time() - start
    print "Took", end_time, "to finish"