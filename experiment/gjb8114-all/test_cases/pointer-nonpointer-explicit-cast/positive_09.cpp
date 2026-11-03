struct Flags {
    bool enabled;
};

int main() {
    int value = 42;
    int* ptr = &value;
    Flags flags{false};
    flags.enabled = static_cast<bool>(ptr);
    return 0;
}
