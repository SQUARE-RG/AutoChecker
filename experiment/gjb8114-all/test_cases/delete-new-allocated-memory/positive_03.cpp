int main() {
    int* p = nullptr;
    p = new int(7);
    *p = 9;
    delete p;
    p = nullptr;
    return 0;
}
