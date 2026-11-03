struct Registry {
    static int value;
};

int Registry::value = 7;

int* get_registry() {
    return &Registry::value;
}

int main() {
    return 0;
}
