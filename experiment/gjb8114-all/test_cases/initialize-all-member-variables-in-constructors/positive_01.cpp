#include <iostream>

class Settings {
public:
    Settings();
    explicit Settings(int level);
    int level() const { return level_; }
    int flags() const { return flags_; }
private:
    int level_;
    int flags_;
};

Settings::Settings() : level_(0), flags_(0) {}

Settings::Settings(int level) : level_(level), flags_(0) {}

int main() {
    Settings defaults;
    Settings custom(3);
    std::cout << defaults.level() << defaults.flags() << ' '
              << custom.level() << custom.flags() << std::endl;
    return 0;
}
