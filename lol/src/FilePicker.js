import React, {useState, useEffect} from 'react'
import { FileDrop } from 'react-file-drop'
import { Typography } from '@mui/material';
import "./f.css"
import axios from 'axios'
import CenteredTabs from "./Table"
import NoteAddOutlinedIcon from '@mui/icons-material/NoteAddOutlined';
import CircularProgress from '@mui/material/CircularProgress';
import { useNavigate } from "react-router-dom";
import Alert from '@mui/material/Alert';

export default function FilePicker() {
    const [isFilePicked, setIsFiledPicked] = useState(false)
    const [data, setData] = useState()
    const [file, setFile] = useState()
    const [alert, setAlert] = useState(["info", "", false])
    let navigate = useNavigate(); 

    // useEffect(() => {
    //   const storedData = window.localStorage.getItem('data')
    //   console.log(storedData)
    //   console.log(storedData === null)
    //   if(typeof storedData !== undefined){
    //     console.log('omg')
    //     setData(JSON.parse(storedData))
    //   }
    // }, []);
    // useEffect(() => {
    //   window.localStorage.setItem('data', JSON.stringify(data));
    // }, [data]);

    const changeHandler = (files, event) => {
      if(typeof files[0] === "undefined" || files[0].type != "text/xml"){
        console.log('File not supported')
        return
      }
      setIsFiledPicked(true)
      if (files[0]) {
        const url = "http://127.0.0.1:8000/"
        // const headers = {
        //   "Access-Control-Allow-Origin":"*", 
        //   "Access-Control-Allow-Headers":"Origin, X-Requested-With, Content-Type, Accept"
        // }
        // const config = {
        //   headers:headers
        // }
        const data = new FormData() 
        data.append('upload_file', files[0])
        setFile(files[0])

        axios.post(url, data).then(res => 
        {
            setData(res.data)
        }); 
      }

    }
//    const onTargetClick = () => {
        //fileInputRef.current.click()
        //console.log(selectedFile)
      //}
    const discard = () => {
      if(window.confirm("Are you sure you want to discard this batch?")){
        setIsFiledPicked(false)
        setData()
      }
    }
    const approveBatch = async() => {
      if(window.confirm("Are you sure you want to approve this batch?")){
        const url = "http://127.0.0.1:8000/"
        const data = new FormData() 
        data.append('upload_file', file)
        const response = await axios.post(url+"approve/", data)
        if(response){
          navigate("/reports")
          navigate(0)
        }
      }
    }
    const approveHandler = async() => {
      approveBatch()
      setData()
      setFile()
      setAlert(["success", "Success! You will now be redirected.", true])
      setTimeout(() => {
        navigate('/reports')
      }, 3000)
    }

    const styles = {border: '1px solid black', width: 600, color: 'black', padding: 20 };
    return (
    <React.Fragment>
        <Typography mt="20px" variant={'h4'} align="center">New Payment</Typography>
        {alert[2] && <Alert severity={alert[0]}>{alert[1]}</Alert>}
        {data? 
        <div style={{marginTop:"20px"}}><CenteredTabs onApprove={approveHandler} onDiscard={discard} data={data}/></div>:
        <div style={{border:"1px dashed grey", marginTop:"20px"}}>
          {!alert[2] &&
          <FileDrop
            onDrop={(files, event) => changeHandler(files, event)}
            >
              {file? <CircularProgress />:<NoteAddOutlinedIcon />}
              <Typography>Drag and Drop XML file</Typography> 
          </FileDrop>
          }
        </div>
        }
    </React.Fragment>
    );
}

