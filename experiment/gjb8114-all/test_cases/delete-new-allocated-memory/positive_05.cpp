int main() {
    int* p = new int(42);
    int value = *p;
    delete p;
    p = nullptr;
    (void)value;
    return 0;
}
