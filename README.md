# OTOSO: Online Trace Ordering for Structural Overviews

Prototype implementation of OTOSO as specified in tba. 

This tool allows to observe an event stream, collecting all event data in a Cuckoo hash table and produce a 2d plot visualization of potentially interesting trace cluster structures.

If you'd like to learn more about how it works, see References below.

Brought to you by Florian Richter (richter@dbs.ifi.lmu.de).


# Usage

To apply OTOSO, you need a log. We are using logs from the BPI Challenge 2015 as an example. You can download them under: https://data.4tu.nl/repository/collection:event_logs_real



# References

The algorithm used by ``OTOSO`` is taken directly from the original paper by Richter, Maldonado, Zellner and Seidl. If you would like to discuss the paper, or corresponding research questions on temporal process mining (we have implemented a few other algorithms as well) please email the authors.
