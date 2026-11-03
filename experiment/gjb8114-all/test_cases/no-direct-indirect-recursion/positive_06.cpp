struct Count {
    int value;
};

Count operator+(const Count& lhs, const Count& rhs) {
    return Count{lhs.value + rhs.value};
}

int main() {
    Count a{1};
    Count b{2};
    Count c = a + b;
    return c.value;
}
