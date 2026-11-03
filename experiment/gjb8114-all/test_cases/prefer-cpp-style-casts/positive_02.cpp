int main() {
    int value = 42;
    const int& readOnly = value;
    int& writable = const_cast<int&>(readOnly);
    writable = 7;
    return value;
}
