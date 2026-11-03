int main() {
    int* p = new int[4]{1, 2, 3, 4};
    int sum = p[0] + p[1];
    delete[] p;
    p = nullptr;
    (void)sum;
    return 0;
}
