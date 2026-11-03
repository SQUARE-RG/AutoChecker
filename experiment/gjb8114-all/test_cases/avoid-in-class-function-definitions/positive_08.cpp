namespace registry {
class Config {
public:
    constexpr int default_value() const;
};
constexpr int Config::default_value() const {
    return 17;
}
}
int main() {
    registry::Config config;
    return config.default_value();
}
