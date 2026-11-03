int main() {
    int value = 1;
    int* first = &value;
    int* second = first;
    int copy = value;
    return *second + copy;
}
