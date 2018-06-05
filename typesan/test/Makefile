all: test01.typesan

%.o: %.cc
	$(CXX) $(CXXFLAGS) -o $@ -c $<

%.typesan : %.o
	$(CXX) $(LDFLAGS) -o $@ $<

.PHONY: test clean

test:
	./test01.typesan

clean:
	 $(RM) *.typesan *.o
