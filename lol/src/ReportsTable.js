import * as React from 'react';
import { useState, useEffect } from 'react';
import { styled } from '@mui/material/styles';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell, { tableCellClasses } from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Reports from './Reports'
import axios from 'axios'


const StyledTableCell = styled(TableCell)(({ theme }) => ({
  [`&.${tableCellClasses.head}`]: {
    backgroundColor: "#e11383",
    color: theme.palette.common.white,
    fontWeight: "bold"
  },
  [`&.${tableCellClasses.body}`]: {
    fontSize: 14,
  },
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  '&:nth-of-type(odd)': {
    backgroundColor: theme.palette.action.hover,
  },
  // hide last border
  '&:last-child td, &:last-child th': {
    border: 0,
  },
}));

function createData(name, calories, fat, carbs, protein) {
  return { name, calories, fat, carbs, protein };
}

const rows = [
  createData('Frozen yoghurt', 159, 6.0, 24, 4.0),
  createData('Ice cream sandwich', 237, 9.0, 37, 4.3),
];

export default function ReportsTable() {
    const [batches, setBatches] = useState([])
    useEffect(() => getBatches(), [])
    const getBatches = () =>{
      const url = "http://127.0.0.1:8000/getCsv/"
      axios.get(url).then(res => 
        {
            console.log(res)
            console.log(res.data.pk)
            setBatches(res.data.batch_list)
        }); 
    }

    // axios request to get batch data.
        
    return (
        <TableContainer>
        <Table sx={{ minWidth: 500 }} aria-label="customized table">
            <TableHead>
            <TableRow>
                <StyledTableCell>Date Approved</StyledTableCell>
                <StyledTableCell>Status</StyledTableCell>
                <StyledTableCell>Payments Remaining</StyledTableCell>
                <StyledTableCell align="right">Generate CSV</StyledTableCell>
            </TableRow>
            </TableHead>
            <TableBody>
            {batches.map((batch) => (
                <StyledTableRow key={batch.batch_id}>
                <StyledTableCell component="th" scope="row">
                    {batch.date_approved}
                </StyledTableCell>
                <StyledTableCell>{batch.status}</StyledTableCell>
                <StyledTableCell align='center'>{batch.payments_remaining}</StyledTableCell>
                <StyledTableCell align="right"><Reports batch_id = {batch.batch_id} status={batch.status}/></StyledTableCell>
                </StyledTableRow>
            ))}
            </TableBody>
        </Table>
        </TableContainer>
    );
}