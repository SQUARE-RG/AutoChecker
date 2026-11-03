int apply(int value) {
    return value * 2;
}

int main() {
    int value = 2;
    int choice = 1;
    switch (choice) {
        case 1:
            ++value;
            break;
        default:
            value--;
            break;
    }
    return apply(value);
}
