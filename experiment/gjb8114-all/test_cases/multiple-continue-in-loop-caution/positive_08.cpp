#include <vector>
#include <cstddef>

int process_commands(const std::vector<int>& commands) {
    int result = 0;
    std::size_t index = 0;
    while (index < commands.size()) {
        int command = commands[index++];
        switch (command) {
            case 0:
                continue;
            case 1:
                result += 1;
                break;
            default:
                result += command;
                break;
        }
    }
    return result;
}
