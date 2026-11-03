int produce() {
    return 42;
}

int main() {
    static_cast<void>(produce());
    return 0;
}
