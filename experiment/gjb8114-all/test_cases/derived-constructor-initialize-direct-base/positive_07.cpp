#include <iostream>

class Document {
public:
    int docid;
    Document() : docid(0) {}
    explicit Document(int v) : docid(v) {}
};

class Book : public Document {
public:
    int bookid;
    Book() try : Document(0), bookid(1)
    {
    } catch (...) {
    }
};

int main() {
    Book mybook;
    std::cout << mybook.docid << mybook.bookid << std::endl;
    return 0;
}
