int main() {
    int x = 3, y = 4, z = 5;
    while ((x > y) != (y < z)) {
        x = 10;
        break;
    }
    return 0;
}
