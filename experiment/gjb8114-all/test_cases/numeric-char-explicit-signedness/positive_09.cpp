class Counter {
public:
    Counter() : count(0) {}
    int next() {
        count++;
        return count + 1;
    }
private:
    signed char count;
};

int main() {
    Counter c;
    return c.next();
}
