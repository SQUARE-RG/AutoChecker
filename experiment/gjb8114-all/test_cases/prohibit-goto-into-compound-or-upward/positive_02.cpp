int main() {
    int x = 0;
    goto after;
    x = 1;
after:
    x = 2;
    return 0;
}
