int main() {
    int* p = nullptr;
    p = new int[4];
    p[0] = 1;
    p[1] = 2;
    p[2] = 3;
    p[3] = 4;
    delete[] p;
    p = nullptr;
    return 0;
}
