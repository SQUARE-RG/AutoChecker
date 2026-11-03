struct Settings {
    int maxSpeed;
    int minSpeed;
};

int main() {
    Settings config{10, 20};
    return config.maxSpeed + config.minSpeed;
}
