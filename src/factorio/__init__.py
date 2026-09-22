from collections import defaultdict
from dataclasses import dataclass, field

from rich.console import Console
from rich.pretty import pprint
from rich.tree import Tree
import pydantic


class Building(pydantic.BaseModel, frozen=True):
    name: str
    crafting_speed: float
    module_slots: int


class BuildingAssemblingMachine(Building):
    pass


class BuildingFurnace(Building):
    pass


building_chemical_plant = Building(name="chemical_plant", crafting_speed=1.0, module_slots=3)
building_oil_refinery = Building(name="oil_refinery", crafting_speed=1.0, module_slots=3)
building_assembling_machine_1 = BuildingAssemblingMachine(name="assembling_machine_1", crafting_speed=0.5, module_slots=0)
building_assembling_machine_2 = BuildingAssemblingMachine(name="assembling_machine_2", crafting_speed=0.75, module_slots=2)
building_assembling_machine_3 = BuildingAssemblingMachine(name="assembling_machine_3", crafting_speed=1.25, module_slots=4)
building_stone_furnace = BuildingFurnace(name="stone_furnace", crafting_speed=1.0, module_slots=0)
building_steel_furnace = BuildingFurnace(name="steel_furnace", crafting_speed=2.0, module_slots=0)
building_electric_furnace = BuildingFurnace(name="electric_furnace", crafting_speed=2.0, module_slots=2)


class Item(pydantic.BaseModel, frozen=True):
    name: str
    raw: bool = pydantic.Field(default=False, repr=False)
    fluid: bool = pydantic.Field(default=False, repr=False)

    @property
    def beltable(self) -> bool:
        """Can this be transported directly on a belt?"""
        # TODO: Is this right? Seems right.
        return not self.fluid


class RecipeInput(pydantic.BaseModel, frozen=True):
    amount: float
    item: Item


class RecipeOutput(pydantic.BaseModel, frozen=True):
    amount: float
    item: Item


class Recipe(pydantic.BaseModel):
    inputs: set[RecipeInput]
    crafting_time: float
    outputs: set[RecipeOutput]
    valid_buildings: set[Building]

    def per_second(
        self,
        *,
        item: Item | None = None,
        crafting_speed: float,
    ) -> float:
        """Calculate the amount that this recipe will create per second, which is

        (crafting_speed * recipe_amount / crafting_time)"""
        if item is None:
            if len(self.outputs) != 1:
                raise ValueError("Must specify 'item' for recipes that have multiple outputs")
            else:
                item = next(iter(self.outputs)).item

        output = None
        for recipe_output in self.outputs:
            if recipe_output.item == item:
                output = recipe_output
                break
        if output is None:
            raise ValueError(f"{item!r} is not in outputs")

        amount_per_second = crafting_speed * output.amount / self.crafting_time

        return amount_per_second


# ================== ITEMS ==================
# Green circuits
item_green_circuit = Item(name="green_circuit")
item_iron_plate = Item(name="iron_plate")
item_copper_cable = Item(name="copper_cable")
item_copper_plate = Item(name="copper_plate")
item_iron_ore = Item(name="iron_ore", raw=True)
item_copper_ore = Item(name="copper_ore", raw=True)

# Red circuits
item_red_circuit = Item(name="red_circuit")
item_plastic_bar = Item(name="plastic_bar")
item_coal = Item(name="coal", raw=True)
item_petroleum_gas = Item(name="petroleum_gas", fluid=True)
item_crude_oil = Item(name="crude_oil", raw=True, fluid=True)

# Blue circuits
item_blue_circuit = Item(name="item_blue_circuit")
item_sulfuric_acid = Item(name="item_sulfuric_acid")
item_sulfur = Item(name="item_sulfur")
item_water = Item(name="item_water", raw=True, fluid=True)

# ================== RECIPES ==================
# Green circuit
recipe_green_circuit = Recipe(
    inputs={
        RecipeInput(item=item_iron_plate, amount=1),
        RecipeInput(item=item_copper_cable, amount=3),
    },
    outputs={RecipeOutput(item=item_green_circuit, amount=1)},
    crafting_time=0.5,
    valid_buildings={
        building_assembling_machine_1,
        building_assembling_machine_2,
        building_assembling_machine_3,
    },
)

recipe_copper_wire = Recipe(
    inputs={RecipeInput(item=item_copper_plate, amount=1)},
    outputs={RecipeOutput(item=item_copper_cable, amount=2)},
    crafting_time=0.5,
    valid_buildings={
        building_assembling_machine_1,
        building_assembling_machine_2,
        building_assembling_machine_3,
    },
)

recipe_copper_plate = Recipe(
    inputs={RecipeInput(item=item_copper_ore, amount=1)},
    outputs={RecipeOutput(item=item_copper_plate, amount=1)},
    crafting_time=3.2,
    valid_buildings={
        building_stone_furnace,
        building_steel_furnace,
        building_electric_furnace,
    },
)

recipe_iron_plate = Recipe(
    inputs={RecipeInput(item=item_iron_ore, amount=1)},
    outputs={RecipeOutput(item=item_iron_plate, amount=1)},
    crafting_time=3.2,
    valid_buildings={
        building_stone_furnace,
        building_steel_furnace,
        building_electric_furnace,
    },
)

# Red circuit
recipe_red_circuit = Recipe(
    inputs={
        RecipeInput(item=item_plastic_bar, amount=2),
        RecipeInput(item=item_copper_cable, amount=4),
        RecipeInput(item=item_green_circuit, amount=2),
    },
    outputs={RecipeOutput(item=item_red_circuit, amount=1)},
    crafting_time=6.0,
    valid_buildings={
        building_assembling_machine_1,
        building_assembling_machine_2,
        building_assembling_machine_3,
    },
)

recipe_plastic_bar = Recipe(
    inputs={
        RecipeInput(item=item_coal, amount=1),
        RecipeInput(item=item_petroleum_gas, amount=20),
    },
    outputs={RecipeOutput(item=item_plastic_bar, amount=2)},
    crafting_time=1,
    valid_buildings={building_chemical_plant},
)

# Basic oil processing
recipe_petroleum_gas = Recipe(
    inputs={RecipeInput(item=item_crude_oil, amount=100)},
    outputs={RecipeOutput(item=item_petroleum_gas, amount=45)},
    crafting_time=5,
    valid_buildings={building_oil_refinery},
)

# Blue circuit
recipe_blue_circuit = Recipe(
    inputs={
        RecipeInput(item=item_green_circuit, amount=20),
        RecipeInput(item=item_red_circuit, amount=2),
        RecipeInput(item=item_sulfuric_acid, amount=5),
    },
    outputs={RecipeOutput(item=item_blue_circuit, amount=1)},
    crafting_time=10,
    valid_buildings={
        building_assembling_machine_2,
        building_assembling_machine_3,
    },
)
recipe_sulfuric_acid = Recipe(
    inputs={
        RecipeInput(item=item_iron_plate, amount=1),
        RecipeInput(item=item_sulfur, amount=5),
        RecipeInput(item=item_water, amount=100),
    },
    outputs={RecipeOutput(item=item_sulfuric_acid, amount=50)},
    crafting_time=1,
    valid_buildings={building_chemical_plant},
)
recipe_sulfur = Recipe(
    inputs={
        RecipeInput(item=item_petroleum_gas, amount=30),
        RecipeInput(item=item_water, amount=30),
    },
    outputs={RecipeOutput(item=item_sulfur, amount=2)},
    crafting_time=1,
    valid_buildings={building_chemical_plant},
)

recipes = {
    # Green circuits
    item_green_circuit: recipe_green_circuit,
    item_iron_plate: recipe_iron_plate,
    item_copper_cable: recipe_copper_wire,
    item_copper_plate: recipe_copper_plate,
    # Red circuits
    item_red_circuit: recipe_red_circuit,
    item_plastic_bar: recipe_plastic_bar,
    item_petroleum_gas: recipe_petroleum_gas,
    # Blue circuits
    item_blue_circuit: recipe_blue_circuit,
    item_sulfuric_acid: recipe_sulfuric_acid,
    item_sulfur: recipe_sulfur,
}


@dataclass
class SupplyNode:
    item: Item
    amount_per_second: float
    children: list["SupplyNode"] = field(default_factory=list)

    def totals(self) -> dict[Item, float]:
        totals: defaultdict[Item, float] = defaultdict(float)
        unvisited = list(self.children)
        while unvisited:
            node = unvisited.pop()
            totals[node.item] += node.amount_per_second
            unvisited.extend(node.children)
        return dict(totals)

    def as_rich_tree(self, *, flattened: bool = False) -> Tree:
        name = self.item.name.removeprefix("item_").replace("_", " ").capitalize()
        rate = f"{self.amount_per_second:,.1f}"
        text = f"[bold magenta]{name}[/bold magenta] - [yellow]{rate}/s[/yellow]"
        if self.item.beltable:
            red_belt_rate = f"{self.amount_per_second / 30:,.1f}"
            text += f" ([red]{red_belt_rate} red belts[/red])"

        tree = Tree(text)
        children = self.children
        if flattened:
            children = []
            for item, amount in sorted(self.totals().items(), key=lambda supply: supply[1], reverse=True):
                children.append(SupplyNode(item, amount))
        for child in children:
            tree.add(child.as_rich_tree())
        return tree


def determine_supplies(
    *,
    target_item: Item,
    target_amount_per_second: float,
    building: Building,
) -> set[tuple[Item, float]]:
    """
    Determine amount of source items needed to generate the desired amount of the target item per second

    Output will be tuples of `(item, amount_per_second)`
    """

    recipe = recipes[target_item]

    output = None
    for __output in recipe.outputs:
        if __output.item == target_item:
            output = __output
            break
    if output is None:
        raise ValueError(f"Nothing in {recipe.outputs} matches {target_item!r}")

    crafts_per_second = target_amount_per_second / output.amount

    rv = set()
    for input in recipe.inputs:
        input_amount = input.amount * crafts_per_second
        input_item = input.item
        rv.add((input_item, input_amount))

    return rv


def determine_supply_tree(
    *,
    target_item: Item,
    target_amount_per_second: float,
    furnace_kind: BuildingFurnace,
    assembling_machine_kind: BuildingAssemblingMachine,
) -> SupplyNode:
    """Expand each dependency separately, keeping the demand from its parent."""
    root = SupplyNode(target_item, target_amount_per_second)

    unvisited = [root]

    while unvisited:
        node = unvisited.pop()
        current_item = node.item
        if current_item.raw:
            continue

        # Determine building. Hacky
        recipe = recipes[current_item]
        building = None

        # Some things require assemblers >= level 2
        # So check if this recipe IS an assembler, but user's choice is INVALID.
        # If so, throw.
        if (assembling_machine_kind not in recipe.valid_buildings) and (building_assembling_machine_2 in recipe.valid_buildings):
            raise ValueError(f"{recipe!r} cannot be made with {assembling_machine_kind}")

        # Everything else normal
        elif assembling_machine_kind in recipe.valid_buildings:
            building = assembling_machine_kind
        elif furnace_kind in recipe.valid_buildings:
            building = furnace_kind
        else:
            # Should only be one legal location for the recipe. Verify.
            assert len(recipe.valid_buildings) == 1, f"Whoops. {recipe.valid_buildings=}"
            building = next(iter(recipe.valid_buildings))

        current_supplies = determine_supplies(
            target_item=current_item,
            target_amount_per_second=node.amount_per_second,
            building=building,
        )
        for item, amount_per_second in sorted(current_supplies, key=lambda supply: supply[0].name):
            child = SupplyNode(item, amount_per_second)
            node.children.append(child)
            unvisited.append(child)

    return root


def determine_supplies_deep(
    *,
    target_item: Item,
    target_amount_per_second: float,
    furnace_kind: BuildingFurnace,
    assembling_machine_kind: BuildingAssemblingMachine,
) -> dict[Item, float]:
    """Return combined ingredient rates across all dependency branches."""
    tree = determine_supply_tree(
        target_item=target_item,
        target_amount_per_second=target_amount_per_second,
        furnace_kind=furnace_kind,
        assembling_machine_kind=assembling_machine_kind,
    )
    return tree.totals()


def main() -> None:
    supplies = determine_supplies(
        target_item=item_green_circuit,
        target_amount_per_second=30,
        building=building_assembling_machine_2,
    )

    pprint(supplies)

    supply_tree = determine_supply_tree(
        target_item=item_blue_circuit,
        target_amount_per_second=30,
        assembling_machine_kind=building_assembling_machine_2,
        furnace_kind=building_steel_furnace,
    )

    Console().rule("Detail")
    Console().print(supply_tree.as_rich_tree())
    Console().rule("Summary")
    Console().print(supply_tree.as_rich_tree(flattened=True))
    # pprint(supply_tree.totals())
