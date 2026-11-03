struct Stop {
    int code;
};

int find_positive(int value) {
    while (1) {
        if (value > 0) {
            return value;
        }
        throw Stop{value};
    }
}

int main() {
    return find_positive(5) == 5 ? 0 : 1;
}
