class Character(object):
    status = "Hero"
    age = 23
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense

    def print_stats(self):
        to_print = "Name: %s, HP: %s, Attack: %s, Defense: %s" % (self.name, self.hp, self.attack, self.defense)
        print(to_print)

    def is_alive(self):
        if self.hp > 0:
            return "Alive:",True
        else:
            return "Alive:",False

    def change_status(self, a):
        self.status = a
        return a
        

class Villain(Character):
    relevancy = "Low"
    def __init__(self, name, hp, attack, defense):
        super(Villain, self).__init__(name, hp, attack, defense)

    def print_stats(self):
        to_print = "Name: %s, HP: %s, Attack: %s, Defense: %s, Relevancy: %s" % (self.name, self.hp, self.attack, self.defense, self.relevancy)
        print(to_print)

    def change_relevancy(self):
        if self.relevancy == "Low":
            self.relevancy = "High"
            return self.relevancy
        else:
            self.relevancy = "Low"
            return self.relevancy

    def alive(self):
        return super(Villain, self).is_alive()


char = Character("Jake", 0, 50, 80)
print(char.is_alive())
print(char.change_status("Hero"))
char.print_stats()
print("\n")
char.age = 15
print(char.age)

print("\n")
vil = Villain("Joker", 0, 80, 50)
vil.change_relevancy()
print(vil.change_relevancy())
print(vil.change_status("Super Villain"))
vil.print_stats()
print(vil.alive())

