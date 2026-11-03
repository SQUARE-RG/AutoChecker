#include <iostream>

class ServerConfig final {
public:
    ServerConfig() : retries_(3), verbose_(false) {}
    ~ServerConfig() = default;
    int retries() const { return retries_; }
    bool verbose() const { return verbose_; }
    void set_retries(int value) { retries_ = value; }
private:
    int retries_;
    bool verbose_;
};

int main() {
    ServerConfig config;
    config.set_retries(5);
    std::cout << config.retries() << ' ' << config.verbose() << '\n';
    return 0;
}
