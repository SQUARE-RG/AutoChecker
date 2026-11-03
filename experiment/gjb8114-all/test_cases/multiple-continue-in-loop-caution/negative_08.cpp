#include <vector>
#include <cstddef>

int handle_commands(const std::vector<int>& commands) {
    int accepted = 0;
    std::size_t index = 0;
    while (index < commands.size()) {
        int command = commands[index++];
        switch (command) {
            case 0:
                continue;
            case 1:
                accepted += 1;
                continue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-3]
            default:
                accepted += command;
                break;
        }
    }
    return accepted;
}
