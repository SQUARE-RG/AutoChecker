int* identity(int* p) {
    return p;
}

int main() {
    int value = 0;
    int* original = &value;
    int* copy = identity(original);
    int number = value;
    return *copy + number;
}
