int main() {
    int number = 7;
    double ratio = static_cast<double>(number);
    int* ptr = &number;
    int* alias = ptr;
    return ratio > 0.0 ? *alias : 0;
}
