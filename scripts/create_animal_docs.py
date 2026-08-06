"""Create 10 sample animal information files for testing RAGbot pipeline."""

from pathlib import Path

ANIMALS = {
    "lion.md": """# African Lion (Panthera leo)
The African lion is an apex predator inhabiting grasslands and savannas of Sub-Saharan Africa.
- Social Structure: Lions are the only cats that live in social groups called prides, consisting of up to 15 lions.
- Roar: A male lion's roar can be heard up to 5 miles (8 kilometers) away.
- Hunting: Female lions (lionesses) perform 80-90% of the pride's hunting, targeting prey like zebras and wildebeests.
- Lifespan: Lions live 10-14 years in the wild.
""",
    "elephant.md": """# African Elephant (Loxodonta africana)
The African elephant is the largest living land mammal on Earth.
- Size & Weight: Adult males can weigh up to 6 metric tons (13,000 lbs) and stand 13 feet tall.
- Trunk Muscles: An elephant's trunk contains over 40,000 individual muscles and zero bones.
- Communication: Elephants communicate over vast distances using low-frequency sound waves called infrasound below human hearing.
- Diet: Herbivorous, consuming up to 300 lbs of grass, bark, and leaves daily.
""",
    "penguin.md": """# Emperor Penguin (Aptenodytes forsteri)
The Emperor penguin is the tallest and heaviest of all living penguin species, native to Antarctica.
- Extreme Survival: Male Emperor penguins incubate a single egg on their feet under a brood pouch during Antarctic winters (-40°C).
- Diving Ability: They can dive deeper than 1,800 feet (550 meters) and hold their breath for over 20 minutes.
- Flightless: Their wings are evolved into stiff, flat flippers ideal for underwater swimming.
""",
    "kangaroo.md": """# Red Kangaroo (Macropus rufus)
The Red Kangaroo is the largest marsupial in the world, native to arid central Australia.
- Hopping Speed: Can reach hopping speeds of over 35 mph (56 km/h) and leap up to 25 feet in a single bound.
- Pouch Development: Female kangaroos give birth to tiny embryos (joeys) that crawl into the pouch to nurse for 8 months.
- Tail Support: The large muscular tail acts as a fifth leg when moving slowly and balances the kangaroo at high speeds.
""",
    "dolphin.md": """# Bottlenose Dolphin (Tursiops truncatus)
Bottlenose dolphins are highly intelligent marine mammals found in warm and temperate oceans.
- Echolocation: Dolphins emit high-frequency click signals to navigate and detect prey underwater using echolocation.
- Unihemispheric Sleep: They sleep with only one hemisphere of their brain at a time, keeping one eye open to breathe at the surface.
- Social Bonds: They form complex pods and display cultural behaviors, tool use (sponging), and individual whistles for names.
""",
    "eagle.md": """# Bald Eagle (Haliaeetus leucocephalus)
The Bald Eagle is a bird of prey native to North America and the national bird of the United States.
- Super Vision: Their eyesight is 4 to 8 times stronger than a human's, allowing them to spot a fish from 2 miles away.
- Nest Architecture: Bald eagles build the largest tree nests of any bird species, reaching up to 10 feet wide and weighing 1 ton.
- Hunting Skill: They dive at speeds up to 100 mph to snatch fish out of rivers with sharp talons.
""",
    "cheetah.md": """# Cheetah (Acinonyx jubatus)
The Cheetah is the fastest land animal on Earth, inhabiting eastern and southern Africa.
- Top Speed: Accelerates from 0 to 60 mph in just 3 seconds, reaching top speeds of 70 mph (112 km/h).
- Non-Retractable Claws: Unlike other cats, cheetahs have non-retractable claws that function like running cleats for grip.
- Physical Adaptations: Large nostrils, expanded lungs, and a flexible spine maximize oxygen intake and stride length during sprints.
""",
    "octopus.md": """# Giant Pacific Octopus (Enteroctopus dofleini)
The Giant Pacific Octopus is the largest octopus species, inhabiting the cold coastal waters of the North Pacific.
- Anatomy: Features 8 arms covered in suckers, 3 hearts, and blue copper-based blood (hemocyanin).
- Camouflage: Can change skin color and texture in milliseconds using specialized skin cells called chromatophores.
- High Intelligence: Capable of solving complex mazes, opening childproof jars, and escaping aquarium tanks.
""",
    "giant_panda.md": """# Giant Panda (Ailuropoda melanoleuca)
The Giant Panda is a bear species endemic to bamboo forests in central China.
- Bamboo Diet: 99% of its diet consists of bamboo, requiring it to eat 26 to 84 lbs (12 to 38 kg) of bamboo every single day.
- Pseudo-Thumb: Has an elongated wrist bone (radial sesamoid) functioning as a thumb to grip bamboo stalks firmly while eating.
- Conservation: Once endangered, successful conservation programs raised their wild population to over 1,800 individuals.
""",
    "gray_wolf.md": """# Gray Wolf (Canis lupus)
The Gray Wolf is a large canine native to wilderness regions of North America, Eurasia, and North Africa.
- Pack Hierarchy: Live in packs of 6-15 wolves led by an alpha male and female pair.
- Long Distance Communication: Wolf howls carry up to 10 miles away to establish territory and locate pack members.
- Stamina Hunting: Pursue large ungulates like moose and elk over long distances until the prey is exhausted.
""",
}


def main():
    target_dir = Path("data/animals")
    target_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in ANIMALS.items():
        file_path = target_dir / filename
        file_path.write_text(content, encoding="utf-8")
        print(f"Created: {file_path}")

    print("\nSuccessfully generated 10 animal documents!")


if __name__ == "__main__":
    main()
