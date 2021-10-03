from .command import Command, CommandException
import numpy as np

@Command.register("maxoutable", "max", usage="maxoutable <current_score> <starting_level> <current_lines>")
class MaxoutableCommand(Command):
    def execute(self, score, level, lines):
        max_score = self.calculate_max_possible_score(int(score), int(level), int(lines))
        if max_score >= 999999:
            self.send_message(f"Still maxoutable. Maximum possible score before 29 is {max_score}")
        else:
            self.send_message(f"Not maxoutable. Maximum possible score before 29 is {max_score}")

    def calculate_max_possible_score(self, score, level, lines):
        next_level = np.minimum(level*10+10, np.maximum(100, level*10-50))
        current_level = level
        if lines < next_level:
            lines_left = next_level - lines
            t_left = np.ceil(lines_left/4.0)
            score += t_left * (1200 * (current_level + 1))
            lines += (t_left*4)
            current_level += 1
        else:
            lines_over = lines - next_level + 1
            extra_levels = np.ceil(lines_over/10.0)
            current_level += extra_levels

        lines = int(lines)
        while current_level < 29:
            old_linestring = str(lines)
            lines += 4
            score += (1200 * (current_level + 1))
            linestring = str(lines)
            if linestring[len(linestring)-2] != old_linestring[len(old_linestring)-2]:
                current_level += 1            
            
        return int(score)
