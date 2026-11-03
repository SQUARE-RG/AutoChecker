struct Counter {
    static inline int total = 0;
};

int main() {
    return Counter::total;
}
