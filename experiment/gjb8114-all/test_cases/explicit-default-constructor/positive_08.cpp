int main() {
    class Local {
    public:
        Local() : value(0) {}
        void set(int v) { value = v; }
        int get() const { return value; }
    private:
        int value;
    };

    Local obj;
    obj.set(4);
    return obj.get();
}
