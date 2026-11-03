#include <iostream>

enum class ConfigStatus { ok, missing };

ConfigStatus read_config(bool file_exists) {
    if (!file_exists) {
        return ConfigStatus::missing;
    }
    return ConfigStatus::ok;
}

int main() {
    if (read_config(false) == ConfigStatus::missing) {
        std::cerr << "config missing\n";
        return 1;
    }
    return 0;
}
