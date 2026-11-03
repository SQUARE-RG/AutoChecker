struct Config {
    int limit;
    int timeout;
};

class Settings {
public:
    explicit Settings(int limit = 0, int timeout = 0) : config_{limit, timeout} {}

    Config& config() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-3]
        return config_;
    }

private:
    Config config_;
};

int main() {
    Settings settings{1, 2};
    Config& exposed = settings.config();
    exposed.limit = 10;
    return 0;
}
