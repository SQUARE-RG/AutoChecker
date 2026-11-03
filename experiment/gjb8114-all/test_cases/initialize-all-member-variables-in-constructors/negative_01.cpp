#include <iostream>

class Settings {
public:
    Settings();
    explicit Settings(int level);
    int level() const { return level_; }
private:
    int level_;
    int flags_;
};

Settings::Settings() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-4]
    level_ = 0;
}

Settings::Settings(int level) : level_(level), flags_(0) {}

int main() {
    Settings defaults;
    Settings custom(3);
    std::cout << defaults.level() << ' ' << custom.level() << std::endl;
    return 0;
}
