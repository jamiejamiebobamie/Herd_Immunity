import random, sys
random.seed(42)
from person import Person
from logger import Logger

class Simulation(object):
    '''
    Main class that will run the herd immunity simulation program.  Expects initialization
    parameters passed as command line arguments when file is run.

    Simulates the spread of a virus through a given population.  The percentage of the
    population that are vaccinated, the size of the population, and the amount of initially
    infected people in a population are all variables that can be set when the program is run.

    _____Attributes______

    logger: Logger object.  The helper object that will be responsible for writing
    all logs to the simulation.

    population_size: Int.  The size of the population for this simulation.

    population: [Person].  A list of person objects representing all people in
        the population.

    next_person_id: Int.  The next available id value for all created person objects.
        Each person should have a unique _id value.

    virus_name: String.  The name of the virus for the simulation.  This will be passed
    to the Virus object upon instantiation.

    mortality_rate: Float between 0 and 1.  This will be passed
    to the Virus object upon instantiation.

    basic_repro_num: Float between 0 and 1.   This will be passed
    to the Virus object upon instantiation.

    vacc_percentage: Float between 0 and 1.  Represents the total percentage of population
        vaccinated for the given simulation.

    current_infected: Int.  The number of currently people in the population currently
        infected with the disease in the simulation.

    total_infected: Int.  The running total of people that have been infected since the
    simulation began, including any people currently infected.

    total_dead: Int.  The number of people that have died as a result of the infection
        during this simulation.  Starts at zero.


    _____Methods_____

    __init__(population_size, vacc_percentage, virus_name, mortality_rate,
     basic_repro_num, initial_infected=1):
        -- All arguments will be passed as command-line arguments when the file is run.
        -- After setting values for attributes, calls self._create_population() in order
            to create the population array that will be used for this simulation.

    _create_population(self, initial_infected):
        -- Expects initial_infected as an Int.
        -- Should be called only once, at the end of the __init__ method.
        -- Stores all newly created Person objects in a local variable, population.
        -- Creates all infected person objects first.  Each time a new one is created,
            increments infected_count variable by 1.
        -- Once all infected person objects are created, begins creating healthy
            person objects.  To decide if a person is vaccinated or not, generates
            a random number between 0 and 1.  If that number is smaller than
            self.vacc_percentage, new person object will be created with is_vaccinated
            set to True.  Otherwise, is_vaccinated will be set to False.
        -- Once len(population) is the same as self.population_size, returns population.
    '''

    def __init__(self, population_size, vacc_percentage, virus_name,
                 mortality_rate, basic_repro_num, initial_infected=1):
        self.population_size = population_size
        self.population = []
        self.total_infected = 0
        self.current_infected = 0
        self.died = 0
        self.survived = 0
        self.uninfected = 0
        self.vaccinated = 0
        self.virus_name = virus_name
        self.mortality_rate = mortality_rate
        self.basic_repro_num = basic_repro_num
        self.file_name = "{}_simulation_pop_{}_vp_{}_infected_{}.txt".format(
            virus_name, population_size, vacc_percentage, initial_infected)
        self.initial_infected = initial_infected
        self.vacc_percentage = vacc_percentage
        self.logger = Logger("log1")
        self.newly_infected = []
        self.population = self._create_population()

    def _create_population(self):
        """Creates and returns a population of Person objects with the correct
        number of infected and vaccinated persons."""
        population = []
        popCounter = 0
        infected_count = 0
        while len(population) != self.population_size:
            if infected_count !=  self.initial_infected:
                population.append(Person(popCounter, False, self.mortality_rate))
                infected_count += 1
                self.current_infected += 1
                self.total_infected += 1
            else:
                if random.uniform(0,1) < self.vacc_percentage:
                    population.append(Person(popCounter, True, None))
                    self.vaccinated +=1
                else:
                    population.append(Person(popCounter, False, None))
            popCounter += 1
        return population

    def _simulation_should_continue(self):
        """Determines whether the simulation should continue based on if there
        are any newly-infected people."""
        if len(self.newly_infected) == 0:
            return False
        else:
            return True

    def run(self):
        """Runs the simulation while should_continue is true. Logs the start
        meta data, the time_step, and masters stats. After the time_step(),
        did_survive_infection Person class method is run on infected to determine
        if they lived or died."""
        self.logger.write_metadata(self.population_size, self.vacc_percentage, self.virus_name, self.mortality_rate, self.basic_repro_num)
        time_step_counter = 0
        should_continue = True
        while should_continue:
            self.time_step()
            self.logger.master_stats(self.died, self.survived, self.vaccinated, self.total_infected, len(self.newly_infected), (len(self.population) - self.died))
            self.logger.log_time_step(time_step_counter)
            time_step_counter += 1
            for person in self.population:
                if person.infected != None:
                    if person.did_survive_infection():
                        self.survived += 1
                        self.vaccinated += 1
                        self.logger.log_survivor(person)
                    else:
                        self.died += 1
                        self.logger.log_death(person)
                    self.current_infected -= 1
            should_continue = self._simulation_should_continue()
            self._infect_newly_infected()
        print("The simulation has ended after " + str(time_step_counter) + " turns.")
        self.logger.master_stats(self.died, self.survived, self.vaccinated, self.total_infected, len(self.newly_infected), (len(self.population) - self.died))

    def time_step(self):
        """For each person in the population that is infected, have them interact
        with 100 unique individuals that are alive and not in self.newly_infected."""
        for i, person in enumerate(self.population):
            if person.infected != None:
                interactions = 0
                peopleInteractedWith = []
                while interactions < 100:
                    target = self.population[random.randint(0, len(self.population)-1)]
                    if target not in peopleInteractedWith and target.is_alive and target not in self.newly_infected:
                        did_infect = self.interaction(self.population[i], target)
                        self.logger.log_interaction(self.population[i], target, did_infect, target.is_vaccinated, target.infected)
                        interactions += 1
                        peopleInteractedWith.append(target)

    def interaction(self, person, random_person):
        """During the interaction get a random float between 0 and 1. If the
        float is less than the reproductive rate of the virus, infect the person
        and return True otherwise return False."""
        if random_person.is_vaccinated == False and random_person.infected == None:
            sick = random.uniform(0,1)
            if sick < self.basic_repro_num:
                self.newly_infected.append(random_person)
                return True
            else:
                return False
        else:
            False

    def _infect_newly_infected(self):
        """For individuals in self.newly_infected, change their infected variable
        to the virus' mortality_rate. Add 1 to both the total infected and current
        infected, and then empty the array self.newly_infected."""
        for sickie in self.newly_infected:
            sickie.infected = self.mortality_rate
            self.current_infected += 1
            self.total_infected += 1
        self.newly_infected = []

if __name__ == "__main__":
    params = sys.argv[1:]
    pop_size = int(params[0])
    vacc_percentage = float(params[1])
    virus_name = str(params[2])
    mortality_rate = float(params[3])
    basic_repro_num = float(params[4])
    if len(params) == 6:
        initial_infected = int(params[5])
    else:
        initial_infected = 1
    simulation = Simulation(pop_size, vacc_percentage, virus_name, mortality_rate,
                            basic_repro_num, initial_infected)
    simulation.run()
