struct Config {
    int limit;
    int timeout;
};

class Settings {
public:
    explicit Settings(int limit = 0, int timeout = 0) : config_{limit, timeout} {}

    Config config() const {
        return config_;
    }

private:
    Config config_;
};

int main() {
    Settings settings{1, 2};
    Config copy = settings.config();
    copy.limit = 10;
    return 0;
}
