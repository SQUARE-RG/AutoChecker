enum Code { first = 10, second = 20 };

Code getCode() {
    return first;
}

int main() {
    Code value = getCode();
    (void)value;
    return 0;
}
