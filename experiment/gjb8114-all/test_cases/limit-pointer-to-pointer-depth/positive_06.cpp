int main() {
    int value = 0;
    int* p = &value;
    auto pp = &p;
    return **pp;
}
